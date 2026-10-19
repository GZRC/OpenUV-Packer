// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <vector>
#include <string>
namespace openuv {
struct Box { double w,h; };
struct Place { double x,y; int rotate; };
struct Result {
    double scale=0;
    std::vector<Place> p;
    std::string algorithm="Shelf";
    int searches=1;
    bool maxrects_skipped=false;
};
Result solve(const std::vector<Box>& boxes,double margin,bool rotate,int strategy);
// quality: 0=Fast, 1=Balanced, 2=High. Bounded to at most two worker threads.
Result solve_best(const std::vector<Box>& boxes,double margin,bool rotate,int workers,int quality=1);
Result improve_maxrects(const std::vector<Box>& boxes,double margin,bool rotate,
                       int order,int heuristic,const Result& baseline,int iterations);
void validate_result(const std::vector<Box>& boxes,double margin,const Result& result);
}
