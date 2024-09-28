#ifndef __DYNBRANCHTRACER_HH__
#define __DYNBRANCHTRACER_HH__

#include <memory>
#include <string>

#include "sim/sim_object.hh"
#include "params/DynBranchTracer.hh"
#include "cpu/o3/dyn_inst_ptr.hh"

namespace gem5
{

namespace branch_prediction 
{
    class BPredUnit;
} // namespace branch_prediction

namespace o3
{

struct UArchSnapshot
{
    virtual ~UArchSnapshot() = default;
};

class DynBranchTracer : public SimObject
{
public:
    using Params = DynBranchTracerParams;
    DynBranchTracer(const DynBranchTracerParams& params); 
    virtual ~DynBranchTracer() = default;
    
    // Creates a Dynamic Instruction Record
    virtual std::unique_ptr<UArchSnapshot> recordUArchState(const DynInstPtr& inst, const branch_prediction::BPredUnit* branchPred) = 0;
   
    // Print Dynamic Branch trace 
    virtual void traceDynBranch(const DynInstPtr& inst) = 0;
    
    virtual void traceObjectAllocation(uint64_t obj_addr, uint64_t ras_top) = 0;
};

} // namespace o3

} // namespace gem5

#endif

