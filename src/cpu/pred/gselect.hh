#ifndef __CPU_PRED_GSELECT_PRED_HH__
#define __CPU_PRED_GSELECT_PRED_HH__

#include <vector>
#include <cstdint>

#include "base/sat_counter.hh"
#include "base/types.hh"
#include "cpu/pred/bpred_unit.hh"
#include "params/GSelectBP.hh"

namespace gem5
{

namespace branch_prediction
{

class GSelectBP : public BPredUnit
{
  public:
    using Params = GSelectBPParams;

    GSelectBP(const Params& params);

    void uncondBranch(ThreadID tid, Addr pc, void * &bp_history) final;

    void squash(ThreadID tid, void *bp_history) final;

    bool lookup(ThreadID tid, Addr instPC, void * &bp_history) final;

    void btbUpdate(ThreadID tid, Addr instPC, void * &bp_history) final;

    void update(ThreadID tid, Addr instPC, bool taken,
                   void *bp_history, bool squashed,
                   const StaticInstPtr &inst, Addr corrTarget) final;

  private:

    struct BranchHistory {
        uint32_t history_reg;

        bool updated_counters;
        uint32_t branch_idx;
        bool pred;
    };

    const Params& m_params;

    const uint32_t m_num_bhts{ 1U << m_params.numHistoryBits };
    
    const uint32_t m_bht_size{ m_params.bhtSize };

    const uint32_t m_local_ctr_bits{ m_params.localCtrBits };

    // Predictor State

    std::vector<uint32_t> history_regs;

    std::vector<std::vector<SatCounter8>> m_counters;

    // Methods

    uint32_t getBHTIndex(Addr pc) const { return pc & (m_bht_size - 1); }

    bool readCounter(uint8_t counter) const { return counter >> (m_params.localCtrBits - 1); }

    void updateHistory(ThreadID tid, bool taken);
};

} // namespace branch_prediction

} // namespace gem5

#endif

