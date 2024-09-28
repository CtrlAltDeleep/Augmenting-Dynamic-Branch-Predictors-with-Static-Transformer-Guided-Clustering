#include "arch/arm/dynbranchtracer.hh"
#include "cpu/o3/dyn_inst.hh"
#include "arch/arm/regs/int.hh"
#include "debug/BranchTrace.hh"

namespace gem5
{

namespace o3
{

static const char *regNames[] = {
    "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
    "r8", "r9", "r10", "fp", "r12", "sp", "lr", "pc",
    "cpsr", "f0", "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14",
    "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22",
    "f23", "f24", "f25", "f26", "f27", "f28", "f29", "f30",
    "f31", "fpscr"
};

static void
print_addr(std::stringstream& outs, Addr addr)
{
    outs << std::hex << addr << ',';
    auto it = loader::debugSymbolTable.findNearest(addr);
    if (it != loader::debugSymbolTable.end()) {
        Addr delta = addr - it->address;
        outs << it->name << '+' << delta;
    } else {
        outs << "unknown";
    }
    
}

static char table_cols[] = "tick,disassembly,"
                           "inst_addr,inst_rel_addr," 
                           "pred_addr,pred_rel_addr,"
                           "jump_addr,jump_rel_addr,"
                           "pred_taken,mispredicted,"
                           "ras,regs,"
                           "virtual,return,call,"
                           "alloc_context"; 

ArmDynBranchTracer::ArmDynBranchTracer(const Params& params)
    : DynBranchTracer(params) {
    m_call_alloc_contexts.push(0);
}

void
ArmDynBranchTracer::traceDynBranch(const DynInstPtr& inst) {
    // !(inst->staticInst->isCondCtrl() || inst->staticInst->))
    if (!debug::BranchTrace || !inst->staticInst->isControl())
        return;
    
    // print header
    if(!m_printed_header && debug::BranchTrace) {
        trace::getDebugLogger()->getOstream() << table_cols << std::endl;
        m_printed_header = true;
    }

    std::unique_ptr<PCStateBase> next_pc(inst->pcState().clone());
    inst->staticInst->advancePC(*next_pc);
    
    std::stringstream outs;
    outs << ",";
    
    // Instruction Disassembly
    outs << '"' << inst->staticInst->disassemble(inst->pcState().instAddr(), &loader::debugSymbolTable) << "\",";

    // Instruction address, Instruction relative address
    print_addr(outs, inst->pcState().instAddr());
    outs << ",";
    
    // Predicted address, Predicted relative address
    print_addr(outs, inst->predPC->instAddr());
    outs << ",";
    
    // Jump address, Jump relative address
    print_addr(outs, next_pc->instAddr());
    outs << ",";

    // Predicted taken, Mispredicted
    outs << inst->readPredTaken() << ',' << (*next_pc!=*inst->predPC) << ','; // inst->mispredicted() << ',';

    auto* uarch_snapshot = dynamic_cast<ArmUArchSnapshot*>(inst->m_pred_uarch_snapshot.get());

    // RAS
    {
        outs << "\"[";
        bool first = true;
        for (auto& addr : uarch_snapshot->ras) {
            if (!first) {
                outs << ",";
            }
            first = false;
            print_addr(outs, addr);
        }
        outs << "]\",";
    }

    // Regs
    {
        for (uint32_t i = 0; i < 15; i++) {
            outs << (i!=0?",":"\"[") << regNames[i] << '=' << std::hex << uarch_snapshot->regs[i];
        }
        outs << "]\",";
    }

    // Virtual
    outs << inst->staticInst->isIndirectCtrl() << ',';
    
    // Return
    outs << inst->staticInst->isReturn() << ',';
    
    // Call
    outs << inst->staticInst->isCall() << ',';

    // Object Allocation Context    
    outs << std::hex << m_call_alloc_contexts.top();

    if (inst->staticInst->isIndirectCtrl() && m_obj_alloc_ras.find(uarch_snapshot->regs[0]) != m_obj_alloc_ras.end()) {
        m_call_alloc_contexts.push(m_obj_alloc_ras[uarch_snapshot->regs[0]]);
    } else if (inst->staticInst->isReturn()) {
        // assert(!m_call_alloc_contexts.empty());
        if (m_call_alloc_contexts.size() != 1) {
            m_call_alloc_contexts.pop(); 
        }
    } else if (inst->staticInst->isCall()) {
        m_call_alloc_contexts.push(m_call_alloc_contexts.top());
    }

    outs << std::endl;

    trace::getDebugLogger()->dprintf(::gem5::curTick(), std::string(), "%s", outs.str().c_str());
    
}


std::unique_ptr<UArchSnapshot>
ArmDynBranchTracer::recordUArchState(const DynInstPtr& inst, const branch_prediction::BPredUnit* branchPred) {

    auto snapshot = std::make_unique<ArmUArchSnapshot>();

    ThreadID tid = inst->threadNumber; 
    const branch_prediction::ReturnAddrStack& ras = branchPred->getRAS()[tid];

    snapshot->ras.reserve(ras.getAddrStack().size());
    int tos = ras.topIdx();
    unsigned used_entries = ras.getUsedEntries();

    for (unsigned i = 0; i < used_entries; i++) {
        const auto& ret_addr = ras.getAddrStack()[tos];
        if (!ret_addr) {
            break;
        }
        snapshot->ras.emplace_back(ret_addr->instAddr());

        if (tos == 0) {
            tos = ras.getAddrStack().size() - 1;
        } else {
            tos--;
        }
    }

    for (uint32_t i = 0; i < 15; i++) {
        snapshot->regs[i] = inst->tcBase()->getReg(ArmISA::intRegClass[i]); 
    }

    return snapshot;
}

void
ArmDynBranchTracer::traceObjectAllocation(uint64_t obj_addr, uint64_t ras_top) {
    m_obj_alloc_ras[obj_addr] = ras_top;  
}

} // namespace o3

} // namespace gem5
