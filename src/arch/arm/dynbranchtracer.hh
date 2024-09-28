#ifndef __ARCH_ARM_DYNBRANCHTRACE_HH__
#define __ARCH_ARM_DYNBRANCHTRACE_HH__

#include <vector>
#include <array>

#include "params/ArmDynBranchTracer.hh"
#include "cpu/o3/dynbranchtracer.hh"
#include <unordered_map>
#include <stack>

namespace gem5
{

namespace o3
{

struct ArmUArchSnapshot : public UArchSnapshot
{     
    std::vector<Addr> ras;
    std::array<uint64_t, 15> regs;
    uint64_t obj_alloc_context;
};

class ArmDynBranchTracer : public DynBranchTracer
{
public:
    using Params = ArmDynBranchTracerParams;
    ArmDynBranchTracer(const Params& params);
    virtual ~ArmDynBranchTracer() = default;

    std::unique_ptr<UArchSnapshot> recordUArchState(const DynInstPtr& inst, const branch_prediction::BPredUnit* branchPred) final;

    void traceDynBranch(const DynInstPtr& inst) final;
    
    void traceObjectAllocation(uint64_t obj_addr, uint64_t ras_top) final;

private: 
    std::unordered_map<uint64_t, uint64_t> m_obj_alloc_ras;
    std::stack<uint64_t> m_call_alloc_contexts;

    bool m_printed_header{ false };
};

} // namespace o3

} // namespace gem5

#endif

