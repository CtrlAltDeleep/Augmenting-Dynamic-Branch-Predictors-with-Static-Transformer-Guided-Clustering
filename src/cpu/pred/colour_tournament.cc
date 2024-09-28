
#include "cpu/pred/colour_tournament.hh"
#include "debug/Coloured.hh"

#include "base/bitfield.hh"
#include "base/intmath.hh"
#include <cmath>

namespace gem5
{

namespace branch_prediction
{
// Static member initializer to load file contents automatically
AddressColourMap ColouredTournamentBP::globalMap = readFileContents("/home/ctrlaltdeleep/gem5/results_gobmk/clusters.txt");
AddressColourMap ColouredTournamentBP::localMap = readFileContents("/home/ctrlaltdeleep/gem5/results_gobmk/takeness_based_clusters.txt");


ColouredTournamentBP::ColouredTournamentBP(const ColouredTournamentBPParams &params)
    : BPredUnit(params),
      localPredictorSize(params.localPredictorSize),
      localCtrBits(params.localCtrBits),
      localCtrs(localPredictorSize, SatCounter8(localCtrBits)),
      localHistoryTableSize(params.localHistoryTableSize),
      localHistoryBits(ceilLog2(params.localPredictorSize)),
      //globalPredictorSize(params.globalPredictorSize >> params.colourBits),
      globalPredictorSize(params.globalPredictorSize),
      globalCtrBits(params.globalCtrBits),
      globalCtrs(globalPredictorSize, std::vector<SatCounter8>(std::pow(2, params.colourBits), SatCounter8(globalCtrBits))),
      globalHistory(params.numThreads,  std::vector<unsigned>(std::pow(2, params.colourBits),0)),
      /*
      globalHistoryBits(
          ceilLog2(params.globalPredictorSize >> params.colourBits ) >
          ceilLog2(params.choicePredictorSize >> params.colourBits) ?
          ceilLog2(params.globalPredictorSize >> params.colourBits) :
          ceilLog2(params.choicePredictorSize >> params.colourBits)),
      */
      globalHistoryBits(
          ceilLog2(params.globalPredictorSize) >
          ceilLog2(params.choicePredictorSize) ?
          ceilLog2(params.globalPredictorSize) :
          ceilLog2(params.choicePredictorSize)),
      //choicePredictorSize(params.choicePredictorSize >> params.colourBits),
      choicePredictorSize(params.choicePredictorSize),
      choiceCtrBits(params.choiceCtrBits),
      choiceCtrs(choicePredictorSize, std::vector<SatCounter8>(std::pow(2, params.colourBits) , SatCounter8(choiceCtrBits))),
      colourBits(params.colourBits),
      localColourBits(params.localColourBits)
{
    if (!isPowerOf2(localPredictorSize)) {
        fatal("Invalid local predictor size!\n");
    }

    if (!isPowerOf2(globalPredictorSize)) {
        fatal("Invalid global predictor size!\n");
    }

    localPredictorMask = mask(localHistoryBits);

    if (!isPowerOf2(localHistoryTableSize)) {
        fatal("Invalid local history table size!\n");
    }

    //Setup the history table for the local table
    localHistoryTable.resize(localHistoryTableSize);

    for (int i = 0; i < localHistoryTableSize; ++i)
        localHistoryTable[i] = 0;

    // Set up the global history mask
    // this is equivalent to mask(log2(globalPredictorSize)
    globalHistoryMask = globalPredictorSize - 1;

    if (!isPowerOf2(choicePredictorSize)) {
        fatal("Invalid choice predictor size!\n");
    }

    // Set up choiceHistoryMask
    // this is equivalent to mask(log2(choicePredictorSize)
    choiceHistoryMask = choicePredictorSize - 1;

    //Set up historyRegisterMask
    historyRegisterMask = mask(globalHistoryBits);

    //Check that predictors don't use more bits than they have available
    if (globalHistoryMask > historyRegisterMask) {
        fatal("Global predictor too large for global history bits!\n");
    }
    if (choiceHistoryMask > historyRegisterMask) {
        fatal("Choice predictor too large for global history bits!\n");
    }

    if (globalHistoryMask < historyRegisterMask &&
        choiceHistoryMask < historyRegisterMask) {
        inform("More global history bits than required by predictors\n");
    }

    // Set thresholds for the three predictors' counters
    // This is equivalent to (2^(Ctr))/2 - 1
    localThreshold  = (1ULL << (localCtrBits  - 1)) - 1;
    globalThreshold = (1ULL << (globalCtrBits - 1)) - 1;
    choiceThreshold = (1ULL << (choiceCtrBits - 1)) - 1;

    auto itG = globalMap.begin();
    const Addr addressG = itG->first;
    const unsigned int colourNumberG = itG->second.first;
    const std::string& disassemblyG = itG->second.second;
    std::string resultG = "SNEAK PEAK GLOBAL: Instruction Address: " + std::to_string(addressG) + ", Colour Number: " + std::to_string(colourNumberG) + ", Disassembly: " + disassemblyG + "\n";
    auto itL = localMap.begin();
    const Addr addressL = itL->first;
    const unsigned int colourNumberL = itL->second.first;
    std::string resultL = "SNEAK PEAK LOCAL: Instruction Address: " + std::to_string(addressL) + ", Colour Number: " + std::to_string(colourNumberL) + "\n";

    DPRINTF(Coloured, resultG.c_str());
    DPRINTF(Coloured, resultL.c_str());

    std::string setup = "SETUP: globalPredictorSize: " + std::to_string(globalPredictorSize) + ", choicePredictorSize: " + std::to_string(choicePredictorSize) + ", globalHistoryBits: " + std::to_string(globalHistoryBits) + "\n";

    DPRINTF(Coloured, setup.c_str());

}

inline
unsigned
ColouredTournamentBP::getColour(Addr &branch_addr, bool local = false)
{   
    if (local){
            // Check if the address is present in the map
        auto it = localMap.find(branch_addr);
        if (it != localMap.end()) {
            // Return the colour number if found
            unsigned colour = it->second.first;
            unsigned colourLowBits = colour & ((1 << localColourBits) - 1); // Get low order colourBits from colourNumber
            return colourLowBits;
        } else {
            return 0; // Uncoloured
        }
    }

    // if we get here, then we want to return global colour

    // Check if the address is present in the map
    auto it = globalMap.find(branch_addr);
    if (it != globalMap.end()) {
        // Return the colour number if found
        unsigned colour = it->second.first;
        unsigned colourLowBits = colour & ((1 << colourBits) - 1); // Get low order colourBits from colourNumber
        return colourLowBits;
        
    } else {
        return 0; // Uncoloured
    }
}

inline
std::string
ColouredTournamentBP::getDissam(Addr &branch_addr)
{
    // Check if the address is present in the map
    auto it = globalMap.find(branch_addr);
    if (it != globalMap.end()) {
        // Return the colour number if found
        return it->second.second;
    } else {
        return " "; // not found
    }
}

inline
unsigned
ColouredTournamentBP::calcLocHistIdx(Addr &branch_addr)
{
    // Get low order bits after removing instruction offset. We then mask with localHistoryTableSize, but also make space for colour bits
    unsigned locHistIdx = (branch_addr >> instShiftAmt) & unsigned(((localHistoryTableSize/std::pow(2,localColourBits))) - 1);
        
    unsigned colourNumber = getColour(branch_addr, true);
    
    // Shift colour bits to top
    unsigned colourShiftedUp = colourNumber << (int(ceil(log2(localHistoryTableSize))) - localColourBits);

    // Perform bitwise XOR operation
    unsigned result = colourShiftedUp^locHistIdx;

    return result;
}

inline
void
ColouredTournamentBP::updateGlobalHistTaken(ThreadID tid, unsigned colour)
{       
    globalHistory[tid][colour] = (globalHistory[tid][colour] << 1) | 1;
    globalHistory[tid][colour] = globalHistory[tid][colour] & historyRegisterMask;
} //TODO: if coloured (e.g. 01), then we need to update globalHistory[tid][colour=01=1] as taken, but also globalHistory[tid][colour=00=0=uncoloured] as taken

inline
void
ColouredTournamentBP::updateGlobalHistNotTaken(ThreadID tid, unsigned colour)
{
    globalHistory[tid][colour] = (globalHistory[tid][colour] << 1);
    globalHistory[tid][colour] = globalHistory[tid][colour] & historyRegisterMask;
} //TODO: if coloured (e.g. 01), then we need to update globalHistory[tid][colour=01=1] as not taken, but also globalHistory[tid][colour=00=0=uncoloured] as not taken

inline
void
ColouredTournamentBP::updateLocalHistTaken(unsigned local_history_idx)
{
    localHistoryTable[local_history_idx] =
        (localHistoryTable[local_history_idx] << 1) | 1;
} //TODO: if coloured (e.g. top bits = 01), then we need to update coloured and uncoloured. but getting 2 local_history_idx's from calcLocHistIdx should take care of that

inline
void
ColouredTournamentBP::updateLocalHistNotTaken(unsigned local_history_idx)
{
    localHistoryTable[local_history_idx] =
        (localHistoryTable[local_history_idx] << 1);
} //TODO: if coloured (e.g. top bits = 01), then we need to update coloured and uncoloured. but getting 2 local_history_idx's from calcLocHistIdx should take care of that


void
ColouredTournamentBP::btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history)
{
    unsigned colourNumber = getColour(branch_addr);
    
    unsigned local_history_idx = calcLocHistIdx(branch_addr);
    //Update Global History to Not Taken (clear LSB)
    globalHistory[tid][0] &= (historyRegisterMask & ~1ULL);
    globalHistory[tid][colourNumber] &= (historyRegisterMask & ~1ULL);

    //Update Local History to Not Taken
    localHistoryTable[local_history_idx] =
       localHistoryTable[local_history_idx] & (localPredictorMask & ~1ULL);
} //TODO: if coloured (e.g. top bits = 01), then calcLocHistIdx returns 2 idx's. both globalHistory[tid][01] and globalHistory[tid][00] are updated. then for both idx's localHistoryTable is updated.

bool
ColouredTournamentBP::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
    // debug
    unsigned colourNumber = getColour(branch_addr);
    std::string dissam = getDissam(branch_addr);
    std::stringstream ss;
    ss << std::hex << branch_addr;
    std::string hexString = ss.str();

    if (colourNumber != 0){
        std::string result = hexString + " : " + std::to_string(colourNumber) + " ->  " + dissam + "\n";
        DPRINTF(Coloured, result.c_str());
    }
    // debug

    bool local_prediction;
    unsigned local_history_idx;
    unsigned local_predictor_idx;

    bool global_prediction;
    bool coloured_global_prediction;
    bool choice_prediction;
    bool colour_choice_prediction;

    //Lookup in the local predictor to get its branch prediction
    local_history_idx = calcLocHistIdx(branch_addr);
    local_predictor_idx = localHistoryTable[local_history_idx]
        & localPredictorMask;
    local_prediction = localCtrs[local_predictor_idx] > localThreshold;

    // TODO: if coloured branch, also look up coloured branch prediction for other local_history_idx. get coloured local pred
    unsigned colour = getColour(branch_addr);

    //Lookup in the global predictor to get its branch prediction
    global_prediction = globalThreshold <
      globalCtrs[globalHistory[tid][0] & globalHistoryMask][0];

    //Lookup in the coloured global predictor to get its branch prediction
    coloured_global_prediction = globalThreshold <
      globalCtrs[globalHistory[tid][colour] & globalHistoryMask][colour];


    // TODO: if coloured branch, also look up coloured branch prediction for globalHistory[tid]. get coloured global pred.
    // Keep all structs the same size as they are rn, but from pc xor 2 least significant bits with colour instead

    //Lookup in the choice predictor to see if we should use local or global strategy
    choice_prediction = choiceThreshold <
      choiceCtrs[globalHistory[tid][0] & choiceHistoryMask][0]; //TODO: maybe instead of indexing choice pred row w/ globalHistory[tid][0], we index with xor of the entire globalHistory[tid] row (or maybe keep indexing the same for local/gloabl choice, but xor for colour choice)
    
    //Lookup in the colour columns of choice predictor to see if colour is useful in global strategy
    colour_choice_prediction = choiceThreshold <
      choiceCtrs[globalHistory[tid][colour] & choiceHistoryMask][colour];


    // Create BPHistory and pass it back to be recorded.
    BPHistory *history = new BPHistory;
    history->globalHistory = globalHistory[tid]; // record/restore all colour history
    history->localPredTaken = local_prediction;
    history->globalPredTaken = global_prediction;
    history->colouredGlobalPredTaken = coloured_global_prediction; // track both uncoloured and coloured pred. if uncoloured, these should be the same so won't impact choice counters later
    history->globalUsed = choice_prediction;
    history->localHistoryIdx = local_history_idx;
    history->localHistory = local_predictor_idx;
    bp_history = (void *)history;
    // TODO: this struct needs to back up uncoloured, but also coloured if branch is coloured

    assert(local_history_idx < localHistoryTableSize);

    // Speculative update of the global history and the
    // selected local history.
    if (choice_prediction) { // we pick global as better here
        if(colour_choice_prediction && colour != 0){ // we use colour as its useful here
            ++stats.globalColouredUsed;
            std::string msg =  "!!! COLOUR " + std::to_string(colour)  + " USEFUL.\n";
            DPRINTF(Coloured, msg.c_str());
            if (coloured_global_prediction) {
                updateGlobalHistTaken(tid, 0);
                if (colour != 0) {updateGlobalHistTaken(tid, colour);} // if to avoid double update on uncoloured braches. not rly needed
                updateLocalHistTaken(local_history_idx);
                return true;
            } else {
                updateGlobalHistNotTaken(tid, 0);
                if (colour != 0) {updateGlobalHistNotTaken(tid, colour);} // if to avoid double update on uncoloured braches. not rly needed
                updateLocalHistNotTaken(local_history_idx);
                return false;
            }
        } else{ // global is better than local, but the colour info is not helpful (or branch is uncoloured)
            ++stats.globalUncolouredUsed;
            if (colour != 0){
                ++stats.globalUncolouredUsedOnColouredBranch;
                std::string msg =  "*** COLOUR " + std::to_string(colour)  + " NOT USEFUL.\n";
                DPRINTF(Coloured, msg.c_str());
            }
            if (global_prediction) {
                updateGlobalHistTaken(tid, 0);
                if (colour != 0) {updateGlobalHistTaken(tid, colour);} // if to avoid double update on uncoloured braches
                updateLocalHistTaken(local_history_idx);
                return true;
            } else {
                updateGlobalHistNotTaken(tid, 0);
                if (colour != 0) {updateGlobalHistNotTaken(tid, colour);} // if to avoid double update on uncoloured braches
                updateLocalHistNotTaken(local_history_idx);
                return false;
            }
        }
        
    } else { // we pick local as better here
        ++stats.localUsed;
        if (local_prediction) {
            updateGlobalHistTaken(tid, 0);
            if (colour != 0) {updateGlobalHistTaken(tid, colour);} // if to avoid double update on uncoloured braches
            updateLocalHistTaken(local_history_idx);
            return true;
        } else {
            updateGlobalHistNotTaken(tid, 0);
            if (colour != 0) {updateGlobalHistNotTaken(tid, colour);} // if to avoid double update on uncoloured braches
            updateLocalHistNotTaken(local_history_idx);
            return false;
        }
    }
}

void
ColouredTournamentBP::uncondBranch(ThreadID tid, Addr pc, void * &bp_history)
{
    // Create BPHistory and pass it back to be recorded.
    BPHistory *history = new BPHistory;
    history->globalHistory = globalHistory[tid];
    history->localPredTaken = true;
    history->globalPredTaken = true;
    history->colouredGlobalPredTaken = true;
    history->globalUsed = true;
    history->localHistoryIdx = invalidPredictorIndex;
    history->localHistory = invalidPredictorIndex;
    bp_history = static_cast<void *>(history);

    unsigned colour = getColour(pc);

    updateGlobalHistTaken(tid, 0);
    if (colour != 0) {updateGlobalHistTaken(tid, colour);}
}

void
ColouredTournamentBP::update(ThreadID tid, Addr branch_addr, bool taken,
                     void *bp_history, bool squashed,
                     const StaticInstPtr & inst, Addr corrTarget)
{
    assert(bp_history);

    BPHistory *history = static_cast<BPHistory *>(bp_history);

    unsigned local_history_idx = calcLocHistIdx(branch_addr);

    assert(local_history_idx < localHistoryTableSize);

    // Unconditional branches do not use local history.
    bool old_local_pred_valid = history->localHistory !=
            invalidPredictorIndex;

    // If this is a misprediction, restore the speculatively
    // updated state (global history register and local history)
    // and update again.
    if (squashed) {
        // Global history restore and update
        for (size_t i = 0; i < globalHistory[tid].size(); ++i) {
            globalHistory[tid][i] = ((history->globalHistory)[i] << 1) | taken;
            globalHistory[tid][i] &= historyRegisterMask;
        }

        // Local history restore and update.
        if (old_local_pred_valid) {
            localHistoryTable[local_history_idx] =
                        (history->localHistory << 1) | taken;
        }

        return;
    }

    unsigned old_local_pred_index = history->localHistory &
        localPredictorMask;

    assert(old_local_pred_index < localPredictorSize);

    // Update the choice predictor to tell it which, of local and global, was correct if
    // there was a prediction.
    if (history->localPredTaken != history->globalPredTaken &&
        old_local_pred_valid)
    {
        // If the local prediction matches the actual outcome,
        // decrement the counter. Otherwise increment the
        // counter.
        unsigned choice_predictor_idx =
            (history->globalHistory)[0] & choiceHistoryMask;
        if (history->localPredTaken == taken) {
            choiceCtrs[choice_predictor_idx][0]--;
        } else if (history->globalPredTaken == taken) {
            choiceCtrs[choice_predictor_idx][0]++;
        }
    }

    unsigned colour = getColour(branch_addr);

    // Update the choice predictor to tell it if colour or uncoloured was correct if
    // there was a prediction.
    if (history->globalPredTaken != history->colouredGlobalPredTaken)
    {
        // If the uncoloured prediction matches the actual outcome,
        // decrement the counter. Otherwise increment the
        // counter.
        unsigned choice_predictor_idx =
            (history->globalHistory)[colour] & choiceHistoryMask;
        if (history->globalPredTaken == taken) {
            choiceCtrs[choice_predictor_idx][colour]--;
        } else if (history->colouredGlobalPredTaken == taken) {
            choiceCtrs[choice_predictor_idx][colour]++;
        }
    }

    // Update the counters with the proper
    // resolution of the branch. Histories are updated
    // speculatively, restored upon squash() calls, and
    // recomputed upon update(squash = true) calls,
    // so they do not need to be updated.
    unsigned global_predictor_idx =
            (history->globalHistory)[0] & globalHistoryMask;
    if (taken) {
        globalCtrs[global_predictor_idx][0]++;
        if (old_local_pred_valid) {
            localCtrs[old_local_pred_index]++;
        }
    } else {
        globalCtrs[global_predictor_idx][0]--;
        if (old_local_pred_valid) {
            localCtrs[old_local_pred_index]--;
        }
    }

    //update coloured history with correct resolution, if applicable
    if (colour != 0){
        unsigned global_predictor_idx = (history->globalHistory)[colour] & globalHistoryMask;
        if (taken) {
            globalCtrs[global_predictor_idx][colour]++;
        } else {
            globalCtrs[global_predictor_idx][colour]--;
        }
    }

    // We're done with this history, now delete it.
    delete history;
}

void
ColouredTournamentBP::squash(ThreadID tid, void *bp_history)
{
    BPHistory *history = static_cast<BPHistory *>(bp_history);

    // Restore global history to state prior to this branch.
    globalHistory[tid] = history->globalHistory;

    // Restore local history
    if (history->localHistoryIdx != invalidPredictorIndex) {
        localHistoryTable[history->localHistoryIdx] = history->localHistory;
    }

    // Delete this BPHistory now that we're done with it.
    delete history;
}

#ifdef DEBUG
int
ColouredTournamentBP::BPHistory::newCount = 0;
#endif

} // namespace branch_prediction
} // namespace gem5
