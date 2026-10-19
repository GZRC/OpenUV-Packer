// SPDX-License-Identifier: GPL-3.0-or-later
#include "openuv.hpp"
#include <algorithm>
#include <future>
#include <stdexcept>
namespace openuv {
Result solve_best(const std::vector<Box>& boxes,double margin,bool rotate,int workers,int quality) {
    if(quality<0 || quality>2)throw std::invalid_argument("Unknown quality preset");
    Result best=solve(boxes,margin,rotate,0);
    auto other=solve(boxes,margin,rotate,1);
    if(other.scale>best.scale)best=other;
    const size_t limits[]={128,256,512};
    const int heuristics[]={1,2,3},iterations[]={20,28,36};
    const int count=heuristics[quality]*2;
    if(boxes.size()>limits[quality]) {
        best.maxrects_skipped=true;best.searches=2;validate_result(boxes,margin,best);return best;
    }
    // Each worker starts from the same best shelf result. Results are reduced in
    // deterministic strategy order, independent of thread scheduling.
    const Result baseline=best;
    std::vector<Result> candidates(count,baseline);
    auto run=[&](int parity,int step){
        for(int i=parity;i<count;i+=step) {
            candidates[i]=improve_maxrects(boxes,margin,rotate,i%2,i/2,baseline,iterations[quality]);
            validate_result(boxes,margin,candidates[i]);
        }
    };
    if(workers>1){auto task=std::async(std::launch::async,[&]{run(1,2);});run(0,2);task.get();}
    else run(0,1);
    for(auto& candidate:candidates)if(candidate.scale>best.scale)best=candidate;
    best.searches=count+2;validate_result(boxes,margin,best);return best;
}
}
