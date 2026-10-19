// SPDX-License-Identifier: GPL-3.0-or-later
// Project-owned implementation of maximal free rectangles; no external packer.
#include "openuv.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <tuple>
namespace openuv {
namespace {
struct Rect { double x,y,w,h; };
bool contains(const Rect& a,const Rect& b) {
    return a.x<=b.x && a.y<=b.y && a.x+a.w>=b.x+b.w && a.y+a.h>=b.y+b.h;
}
bool overlaps(const Rect& a,const Rect& b) {
    return a.x<b.x+b.w && b.x<a.x+a.w && a.y<b.y+b.h && b.y<a.y+a.h;
}
bool place(const std::vector<Box>& boxes,const std::vector<size_t>& order,
           double margin,bool rotate,int heuristic,double scale,std::vector<Place>& output) {
    std::vector<Rect> free{{0,0,1,1}};
    output.resize(boxes.size());
    for(size_t index:order) {
        Rect chosen{}; int chosen_rotation=0; bool found=false;
        auto score_best=std::tuple{std::numeric_limits<double>::infinity(),0.,0.,0.,0};
        for(const auto& slot:free) for(int r=0;r<=(rotate ? 1:0);++r) {
            double w=(r?boxes[index].h:boxes[index].w)*scale+2*margin;
            double h=(r?boxes[index].w:boxes[index].h)*scale+2*margin;
            if(w>slot.w || h>slot.h)continue;
            const double dx=slot.w-w,dy=slot.h-h;
            double a,b;
            if(heuristic==0){a=std::min(dx,dy);b=std::max(dx,dy);} // short-side fit
            else if(heuristic==1){a=slot.w*slot.h-w*h;b=std::min(dx,dy);} // area fit
            else {a=slot.y+h;b=slot.x;} // bottom-left
            auto score=std::tuple{a,b,slot.y,slot.x,r};
            if(score<score_best){score_best=score;chosen={slot.x,slot.y,w,h};chosen_rotation=r;found=true;}
        }
        if(!found)return false;
        output[index]={chosen.x+margin,chosen.y+margin,chosen_rotation};
        std::vector<Rect> split;
        for(const auto& slot:free) {
            if(!overlaps(slot,chosen)){split.push_back(slot);continue;}
            // Split every intersecting free rectangle, not just the chosen slot.
            // Remaining free rectangles may overlap each other, never occupied space.
            if(chosen.x>slot.x)split.push_back({slot.x,slot.y,chosen.x-slot.x,slot.h});
            if(chosen.x+chosen.w<slot.x+slot.w)
                split.push_back({chosen.x+chosen.w,slot.y,slot.x+slot.w-chosen.x-chosen.w,slot.h});
            if(chosen.y>slot.y)split.push_back({slot.x,slot.y,slot.w,chosen.y-slot.y});
            if(chosen.y+chosen.h<slot.y+slot.h)
                split.push_back({slot.x,chosen.y+chosen.h,slot.w,slot.y+slot.h-chosen.y-chosen.h});
        }
        free.clear();
        for(size_t i=0;i<split.size();++i) {
            if(split[i].w<=0 || split[i].h<=0)continue;
            bool redundant=false;
            for(size_t j=0;j<split.size();++j)if(i!=j && contains(split[j],split[i])) {
                if(!contains(split[i],split[j]) || j<i){redundant=true;break;}
            }
            if(!redundant)free.push_back(split[i]);
        }
        // Bound pathological fragmentation; abandon this candidate, keep baseline.
        if(free.size()>4096)return false;
    }
    return true;
}
}
Result improve_maxrects(const std::vector<Box>& boxes,double margin,bool rotate,
                       int ordering,int heuristic,const Result& baseline,int iterations) {
    std::vector<size_t> order(boxes.size());std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](size_t a,size_t b){
        auto key=[&](Box v){return ordering==0 ? v.w*v.h:std::max(v.w,v.h);};
        return key(boxes[a])>key(boxes[b]);
    });
    // Conservative area/side bound in original UV units, avoiding a zero-scale trial.
    double area=0,largest=0;
    for(auto box:boxes){area+=box.w*box.h;largest=std::max({largest,box.w,box.h});}
    double upper=std::min(1/std::sqrt(area),(1-2*margin)/largest);
    Result best=baseline;
    if(!std::isfinite(upper) || upper<=baseline.scale)return best;
    double low=baseline.scale,high=upper;
    std::vector<Place> placement;
    // A candidate failing at baseline may still succeed at a larger scale because
    // heuristic feasibility is not monotone. Probe the full interval before refinement.
    for(int k=8;k>=1;--k) {
        double scale=baseline.scale+(upper-baseline.scale)*k/8.;
        if(place(boxes,order,margin,rotate,heuristic,scale,placement)) {
            low=scale;best.scale=scale;best.p=placement;break;
        }
    }
    for(int k=0;k<iterations;++k) {
        double scale=(low+high)/2;
        if(place(boxes,order,margin,rotate,heuristic,scale,placement)) {
            low=scale;best.scale=scale;best.p=placement;
        }else high=scale;
    }
    if(best.scale>baseline.scale) {
        best.scale*=1-1e-12;
        best.algorithm=std::string("MaxRects-")+(heuristic==0?"BSSF":heuristic==1?"BAF":"BL")+
                       (ordering==0?"-Area":"-Side");
        if(best.scale<=baseline.scale)return baseline;
    }
    return best;
}
}
