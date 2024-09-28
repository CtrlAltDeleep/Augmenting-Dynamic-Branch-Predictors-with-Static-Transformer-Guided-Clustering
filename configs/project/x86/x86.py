import m5
from m5.objects import *
import argparse

class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        raise NotImplementedError

class L1ICache(L1Cache):
    size = '16kB'

    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

class L1DCache(L1Cache):
    size = '64kB'

    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port

class L2Cache(Cache):
    size = '256kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports


binaries = { 'go' : '/home/as8319/benchmarks/specint95/099.go/exe/base/go.base',
    'm88ksim' : '/home/as8319/benchmarks/specint95/124.m88ksim/exe/base/m88ksim.base',
    'gcc' : '/home/as8319/benchmarks/specint95/126.gcc/exe/base/cc1.base' }

args = {
    'go_4_4' : [binaries['go'], 4, 4],
    'm88ksim' : [binaries['m88ksim']],
    'gcc' : [binaries['gcc'], '-quiet', '-funroll-loops', '-fforce-mem', '-fcse-follow-jumps', 
                '-fcse-skip-blocks', '-fexpensive-optimizations', '-fstrength-reduce', '-fpeephole', 
                '-fschedule-insns', '-finline-functions', '-fschedule-insns2',
                '-O', '/home/as8319/benchmarks/specint95/126.gcc/data/test/input/cccp.i', 
                '-o', '/home/as8319/benchmarks/specint95/126.gcc/data/test/input/cccp.s']
}

def parse_arguments():
    parser = argparse.ArgumentParser(
                    prog='Project Gem5 Config Script',
                    description='Run ARM experiemnts')
    parser.add_argument('--exp',
                    choices=args.keys(),
                    help='Run premade experiemnt', required=True)
    
    parser.add_argument('-q', '--quiet',
                    action='store_true',
                    help='Run quiet experiemnt')
    
    parsed_args = parser.parse_args()
    return args[parsed_args.exp], parsed_args.quiet

system = System()

# Basic Setup
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8GB')]

# O3 CPU Setup
system.cpu = X86O3CPU()

# Predictor
# system.cpu.branchPred = GSelectBP()

# system.cpu.branchTracer = ArmDynBranchTracer()

# Caches

# L1D & L1I
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.l2bus = L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# L2 unified
system.l2cache = L2Cache()
system.l2cache.connectCPUSideBus(system.l2bus)

system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

#binary = '/home/as8319/benchmarks/specint95/099.go/exe/base/go.base'
#data_path = '/home/as8319/benchmarks/specint95/099.go/data/ref/input/5stone21.in'

#binary = '/home/as8319/benchmarks/specint95/124.m88ksim/exe/base/m88ksim.base'

cmd, quiet = parse_arguments()

system.workload = SEWorkload.init_compatible(cmd[0])

process = Process()
process.cmd = cmd #[binary, '4', '4'] # [binary, '50', '21', data_path]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()
if not quiet:
    print("Beginning simulation!")
exit_event = m5.simulate()
if not quiet:
    print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))


