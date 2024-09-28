
#ifndef __CPU_PRED_COLOURED_TOURNAMENT_PRED_HH__
#define __CPU_PRED_COLOURED_TOURNAMENT_PRED_HH__

#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>


#include "base/sat_counter.hh"
#include "base/types.hh"
#include "cpu/pred/bpred_unit.hh"
#include "params/ColouredTournamentBP.hh"

namespace gem5
{

namespace branch_prediction
{
using AddressColourMap = std::unordered_map<Addr, std::pair<unsigned int, std::string>>;

static AddressColourMap readFileContents(const std::string& filename) {
    AddressColourMap addressColourMap;

    std::ifstream file(filename);
    if (!file.is_open()) {
        fatal("Error: Unable to open file with colour labels\n");
    }

    std::string line;
    std::getline(file, line);
    bool extendedFormat = (line.find("disassembly") != std::string::npos);

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string token;

        // Parse the line
        std::vector<std::string> tokens;
        while (iss >> token) {
            tokens.push_back(token);
        }

        if (extendedFormat && tokens.size() < 4) {
            // Invalid line format, skip
            continue;
        } else if (!extendedFormat && tokens.size() < 2) {
            // Invalid line format, skip
            continue;
        }

        // Extract the instruction address
        Addr address = std::stoull(tokens[0]);

        if (extendedFormat) {
            // Extract the cluster colour and number
            unsigned int colourNumber = std::stoul(tokens[tokens.size() - 1]) + 1; // add one so colour 0 becomes 1
            std::string colour = tokens[tokens.size() - 2];

            // Merge the remaining segments for disassembly
            std::string disassembly;
            for (size_t i = 1; i < tokens.size() - 2; ++i) {
                disassembly += tokens[i];
                if (i != tokens.size() - 3) {
                    disassembly += " ";
                }
            }

            // Store in the map
            addressColourMap[address] = std::make_pair(colourNumber, disassembly);
        } else {
            // In the shorter format, save disassembly as empty string
            addressColourMap[address] = std::make_pair(std::stoul(tokens[1]) + 1, "");
        }
    }

    return addressColourMap;
}


/**
 * Implements a tournament branch predictor, hopefully identical to the one
 * used in the 21264.  It has a local predictor, which uses a local history
 * table to index into a table of counters, and a global predictor, which
 * uses a global history to index into a table of counters.  A choice
 * predictor chooses between the two.  Both the global history register
 * and the selected local history are speculatively updated.
 */
class ColouredTournamentBP : public BPredUnit
{
  public:
    /**
     * Default branch predictor constructor.
     */
    ColouredTournamentBP(const ColouredTournamentBPParams &params);

    /**
     * Looks up the given address in the branch predictor and returns
     * a true/false value as to whether it is taken.  Also creates a
     * BPHistory object to store any state it will need on squash/update.
     * @param branch_addr The address of the branch to look up.
     * @param bp_history Pointer that will be set to the BPHistory object.
     * @return Whether or not the branch is taken.
     */
    bool lookup(ThreadID tid, Addr branch_addr, void * &bp_history);

    /**
     * Records that there was an unconditional branch, and modifies
     * the bp history to point to an object that has the previous
     * global history stored in it.
     * @param bp_history Pointer that will be set to the BPHistory object.
     */
    void uncondBranch(ThreadID tid, Addr pc, void * &bp_history);
    /**
     * Updates the branch predictor to Not Taken if a BTB entry is
     * invalid or not found.
     * @param branch_addr The address of the branch to look up.
     * @param bp_history Pointer to any bp history state.
     * @return Whether or not the branch is taken.
     */
    void btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history);
    /**
     * Updates the branch predictor with the actual result of a branch.
     * @param branch_addr The address of the branch to update.
     * @param taken Whether or not the branch was taken.
     * @param bp_history Pointer to the BPHistory object that was created
     * when the branch was predicted.
     * @param squashed is set when this function is called during a squash
     * operation.
     * @param inst Static instruction information
     * @param corrTarget Resolved target of the branch (only needed if
     * squashed)
     */
    void update(ThreadID tid, Addr branch_addr, bool taken, void *bp_history,
                bool squashed, const StaticInstPtr & inst, Addr corrTarget);

    /**
     * Restores the global branch history on a squash.
     * @param bp_history Pointer to the BPHistory object that has the
     * previous global branch history in it.
     */
    void squash(ThreadID tid, void *bp_history);

    static AddressColourMap globalMap;
    static AddressColourMap localMap;

  private:
    /**
     * Returns if the branch should be taken or not, given a counter
     * value.
     * @param count The counter value.
     */
    inline bool getPrediction(uint8_t &count);

    /**
     * Returns the local history index, given a branch address.
     * @param branch_addr The branch's PC address.
     */
    inline unsigned calcLocHistIdx(Addr &branch_addr);

    /** Updates global history as taken. */
    inline void updateGlobalHistTaken(ThreadID tid, unsigned colour);

    /** Updates global history as not taken. */
    inline void updateGlobalHistNotTaken(ThreadID tid, unsigned colour);

    /**
     * Updates local histories as taken.
     * @param local_history_idx The local history table entry that
     * will be updated.
     */
    inline void updateLocalHistTaken(unsigned local_history_idx);

    /**
     * Updates local histories as not taken.
     * @param local_history_idx The local history table entry that
     * will be updated.
     */
    inline void updateLocalHistNotTaken(unsigned local_history_idx);

    /**
     * Fetches the colour of this branch.
     * @param branch_addr The address of the branch to find colour of.
     */
    inline unsigned getColour(Addr &branch_addr, bool local);

    /**
     * Fetches the dissam of this branch. (for Debugging)
     * @param branch_addr The address of the branch to find colour of.
     */
    inline std::string getDissam(Addr &branch_addr);

    /**
     * The branch history information that is created upon predicting
     * a branch.  It will be passed back upon updating and squashing,
     * when the BP can use this information to update/restore its
     * state properly.
     */
    struct BPHistory
    {
#ifdef DEBUG
        BPHistory()
        { newCount++; }
        ~BPHistory()
        { newCount--; }

        static int newCount;
#endif
        std::vector<unsigned> globalHistory;
        unsigned localHistoryIdx;
        unsigned localHistory;
        bool localPredTaken;
        bool globalPredTaken;
        bool colouredGlobalPredTaken;
        bool globalUsed;
    };

    /** Flag for invalid predictor index */
    static const int invalidPredictorIndex = -1;
    /** Number of counters in the local predictor. */
    unsigned localPredictorSize;

    /** Mask to truncate values stored in the local history table. */
    unsigned localPredictorMask;

    /** Number of bits of the local predictor's counters. */
    unsigned localCtrBits;

    /** Local counters. */
    std::vector<SatCounter8> localCtrs;

    /** Array of local history table entries. */
    std::vector<unsigned> localHistoryTable;

    /** Number of entries in the local history table. */
    unsigned localHistoryTableSize;

    /** Number of bits for each entry of the local history table. */
    unsigned localHistoryBits;

    /** Number of entries in the global predictor. */
    unsigned globalPredictorSize;

    /** Number of bits of the global predictor's counters. */
    unsigned globalCtrBits;

    /** Per colour array of counters that make up the global predictor. */
    std::vector<std::vector<SatCounter8>> globalCtrs;

    /** Global history register. Contains as much history as specified by
     *  globalHistoryBits. Actual number of bits used is determined by
     *  globalHistoryMask and choiceHistoryMask.
     *  column 0 is for colour 0 (uncoloured). Then column n is for colour n (after bit mask)*/
    std::vector<std::vector<unsigned>> globalHistory;

    /** Number of bits for the global history. Determines maximum number of
        entries in global and choice predictor tables. */
    unsigned globalHistoryBits;

    /** Mask to apply to globalHistory to access global history table.
     *  Based on globalPredictorSize.*/
    unsigned globalHistoryMask;

    /** Mask to apply to globalHistory to access choice history table.
     *  Based on choicePredictorSize.*/
    unsigned choiceHistoryMask;

    /** Mask to control how much history is stored. All of it might not be
     *  used. */
    unsigned historyRegisterMask;

    /** Number of entries in the choice predictor. */
    unsigned choicePredictorSize;

    /** Number of bits in the choice predictor's counters. */
    unsigned choiceCtrBits;

    /** Array of Array of counters that make up the choice predictor. 
     * choice counters in column 0 decide to use global or local. (normal choice pred)
     * choice counters in column n decide to use global History 0 or global History colour n. (decides if colour n info is useful)
    */
    std::vector<std::vector<SatCounter8>> choiceCtrs;

    /** Thresholds for the counter value; above the threshold is taken,
     *  equal to or below the threshold is not taken.
     */
    unsigned localThreshold;
    unsigned globalThreshold;
    unsigned choiceThreshold;

    unsigned colourBits; // number of bits used for global colour information
    unsigned localColourBits; // number of bits used for local colour information

};

} // namespace branch_prediction
} // namespace gem5


#endif // __CPU_PRED_COLOURED_TOURNAMENT_PRED_HH__