import argparse
from m5.objects import *
from m5.stats import dump, reset
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import PrivateL1SharedL2CacheHierarchy
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.utils.simpoint import SimPoint
from pathlib import Path
from project_workloads import suites, build_workload
import m5.trace

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Project Gem5 Config Script',
                    description='Run ARM experiemnts')

    parser.add_argument('--suite',
                    choices=suites.keys(),
                    help='Select benchmark suite', required=True)

    parser.add_argument('--exp',
                    type=str,
                    help='Select benchmark within suite', required=True)
    
    parser.add_argument('--idx',
                    type=int,
                    default=0,
                    help='Select input index')
    
    parser.add_argument('-q', '--quiet',
                    action='store_true',
                    help='Run quiet experiemnt')
    parser.add_argument(
        "-m",
        "--max-ticks",
        type=int,
        default=m5.MaxTick,
        metavar="TICKS",
        help="Run to absolute simulated tick "
        "specified including ticks from a restored checkpoint",
    )
    
    parser.add_argument(
        "--max-instructions",
        type=int,
        default=None,
        help="Set the maximum number of instructions to be simulated"
    )

    parser.add_argument(
        "--load-simpoint-checkpoints",
        type=str,
        default=None,
        help='path to the simpoint checkpoints folder to be loaded'
    )

    parser.add_argument(
        "--checkpoints-path",
        type=str,
        default=None,
        help='path to the simpoint checkpoints folder to be loaded'
    )
    
    parser.add_argument(
        "--checkpoint-idx",
        type=int,
        help='Simpoint checkpoint index'
    )

    parser.add_argument(
        "--warmup-interval",
        type=int,
        help='Simpoint warmup time'
    )
    
    parser.add_argument(
        "--simpoint-interval",
        type=int,
        help='Simpoint interval time'
    )

    
    return parser.parse_args() 

simpoints   = None
def max_inst(warmed_up):
    while True:
        if warmed_up:
            print("End of SimPoint interval")
            yield True
        else:
            print("End of warmup, starting to simulate SimPoint")
            warmed_up = True
            # Schedule a MAX_INSTS exit event during the simulation
            simulator.schedule_max_insts(
                simpoints.get_simpoint_interval()
            )
            dump()
            reset()
            m5.trace.enable()
            yield False

def do_nothing():
    while True:
        yield False

requires(isa_required=ISA.ARM)

args = parse_args()

cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size = '64kB',
    l1i_size = '16kB',
    l2_size  = '256kB'
)

memory = SingleChannelDDR3_1600(size="8GB")

processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.ARM, num_cores=1)
processor.get_cores()[0].get_simobject().branchPred = TAGE_SC_L_64KB()
processor.get_cores()[0].get_simobject().branchTracer = ArmDynBranchTracer()

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

checkpoints = None 
if args.load_simpoint_checkpoints:
    simpoints= SimPoint(
        simpoint_interval=args.simpoint_interval,
        simpoint_file_path=args.load_simpoint_checkpoints + '/simpoints.txt',
        weight_file_path=args.load_simpoint_checkpoints + '/simpoint_weights.txt',
        warmup_interval=args.warmup_interval
    )
    checkpoints = Path(args.checkpoints_path + f'/cpt.SimPoint{args.checkpoint_idx}') 

board.set_workload(build_workload(suites[args.suite], args.exp, args.idx, checkpoints=checkpoints))

on_exit_event = None
if args.load_simpoint_checkpoints:
    on_exit_event = { ExitEvent.MAX_INSTS: max_inst(simpoints.get_warmup_list()[args.checkpoint_idx] == 0) }

simulator = Simulator(
    board=board,
    on_exit_event=on_exit_event
)

if args.load_simpoint_checkpoints:
    if simpoints.get_warmup_list()[args.checkpoint_idx] == 0:
        simulator.schedule_max_insts(args.simpoint_interval)
        print("Warmup not required, starting to simulate SimPoint directly")
    else:
        simulator.schedule_max_insts(simpoints.get_warmup_list()[args.checkpoint_idx])
        m5.trace.disable()
    simulator.run()
else:
    if args.max_instructions:
        simulator.schedule_max_insts(args.max_instructions)
    simulator.run(max_ticks=args.max_ticks)

print(
    "Exiting @ tick {} because {}.".format(
        simulator.get_current_tick(), simulator.get_last_exit_event_cause()
    )
)
