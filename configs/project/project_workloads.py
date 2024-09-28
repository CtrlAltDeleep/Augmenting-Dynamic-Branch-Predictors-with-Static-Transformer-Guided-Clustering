from gem5.resources.workload import CustomWorkload
from gem5.resources.resource import CustomResource
from spec2006_workloads import Spec2006TrainBenchmarks, Spec2006TestBenchmarks, Spec2006RefBenchmarks

SPEC_BASE = '/home/as8319/benchmarks/specCPU2006/benchspec/CPU2006/'

suites = { 'spec2006_train' : Spec2006TrainBenchmarks(SPEC_BASE),
           'spec2006_test' : Spec2006TestBenchmarks(SPEC_BASE),
           'spec2006_ref' : Spec2006RefBenchmarks(SPEC_BASE) }

def build_workload(suite, name, idx, simpoint=None, checkpoints=None) -> CustomWorkload:
    
    workload_exe, workload_params = suite.get_workload_spec(name, idx)

    params = {}
    params['binary'] = CustomResource(workload_exe)
    params['arguments'] = workload_params.args

    if simpoint is not None:
        params['simpoint'] = simpoint

    if checkpoints is not None:
        params['checkpoint'] = checkpoints

    if workload_params.stdin:
        params['stdin_file'] = CustomResource(workload_params.stdin)

    return CustomWorkload(
        function   = 'set_se_binary_workload' if simpoint is None else 'set_se_simpoint_workload',
        parameters = params
    )
