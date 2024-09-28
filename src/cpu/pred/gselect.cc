#include "gselect.hh"

namespace gem5
{

namespace branch_prediction
{

GSelectBP::GSelectBP(const Params& params)
    : BPredUnit(params)
    , m_params(params)
    , history_regs(params.numThreads, 0) {

   m_counters.reserve(m_num_bhts);
   
   for (uint32_t i = 0; i < m_num_bhts; i++) {
       m_counters.emplace_back(m_bht_size, SatCounter8(m_local_ctr_bits));
   }
}

void
GSelectBP::uncondBranch(ThreadID tid, Addr pc, void * &bp_history) {
   BranchHistory* history = new BranchHistory();
   history->history_reg = history_regs[tid];
   history->updated_counters = false;
   history->pred = true;

   bp_history = static_cast<void*>(history);
   
   updateHistory(tid, true);
}

void
GSelectBP::squash(ThreadID tid, void *bp_history) {
    BranchHistory* history = static_cast<BranchHistory*>(bp_history);

    history_regs[tid] = history->history_reg;

    if (history->updated_counters) {
        if (history->pred) {
            m_counters[history->history_reg][history->branch_idx]--;
        } else {
            m_counters[history->history_reg][history->branch_idx]++;
        }
    }

    delete history;
}

bool 
GSelectBP::lookup(ThreadID tid, Addr instPC, void * &bp_history) {
   
    BranchHistory* history = new BranchHistory();
    bp_history = static_cast<void*>(history);
    
    history->history_reg = history_regs[tid];  
    history->branch_idx = getBHTIndex(instPC);

    SatCounter8& counter = m_counters[history_regs[tid]][history->branch_idx];

    history->updated_counters = !(counter.isSaturated() || counter == 0);
    bool prediction = readCounter(counter); 
    history->pred = prediction; 

    updateHistory(tid, prediction);

    // update the counter
    if (prediction) {
        counter++;
    } else {
        counter--;
    }

    return prediction; 
}

void
GSelectBP::btbUpdate(ThreadID tid, Addr instPC, void * &bp_history) {
    history_regs[tid] = history_regs[tid] & ~1U;
    
    BranchHistory* history = static_cast<BranchHistory*>(bp_history);
    assert(history->pred);
    
    SatCounter8& counter = m_counters[history->history_reg][history->branch_idx];

    if (history->updated_counters) {
        counter--; // undo the increment of the prediction
    }
    history->updated_counters = counter != 0;
    counter--; // correct counter update
}

void
GSelectBP::update(ThreadID tid, Addr instPC, bool taken,
            void *bp_history, bool squashed,
            const StaticInstPtr &inst, Addr corrTarget) {

    if (squashed) {
        return;
    }

    BranchHistory* history = static_cast<BranchHistory*>(bp_history);    

    if (history->pred != taken) {
        SatCounter8& counter = m_counters[history->history_reg][history->branch_idx];
        if (history->updated_counters) {
            if (history->pred) {
                counter--;
            } else {
                counter++;
            }
        }
        if (taken) {
            counter++;
        } else {
            counter--;
        }
        history->updated_counters = true;
    }
}

void
GSelectBP::updateHistory(ThreadID tid, bool taken) {
    history_regs[tid] = (history_regs[tid] << 1) | ((uint32_t) taken);
    history_regs[tid] &= m_num_bhts - 1;
}

} // namespace branch_prediction

} // namespace gem5

