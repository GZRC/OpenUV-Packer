// SPDX-License-Identifier: GPL-3.0-or-later
#include "openuv.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace openuv {
void validate_result(const std::vector<Box>& boxes,double margin,const Result& result) {
    if(!std::isfinite(result.scale) || result.scale<=0 || result.p.size()!=boxes.size())
        throw std::runtime_error("Invalid packing result");
    struct Rect{double x,y,right,top;};std::vector<Rect> rects,active;
    constexpr double eps=1e-9;
    for(size_t i=0;i<boxes.size();++i) {
        auto p=result.p[i];auto b=boxes[i];if(p.rotate)std::swap(b.w,b.h);
        Rect r{p.x-margin,p.y-margin,p.x+b.w*result.scale+margin,p.y+b.h*result.scale+margin};
        if(!std::isfinite(r.x)||!std::isfinite(r.y)||!std::isfinite(r.right)||!std::isfinite(r.top)||
           r.x < -eps || r.y < -eps || r.right>1+eps || r.top>1+eps)
            throw std::runtime_error("Packing outside target tile");
        rects.push_back(r);
    }
    std::sort(rects.begin(),rects.end(),[](auto a,auto b){return a.x<b.x;});
    for(auto r:rects) {
        std::erase_if(active,[&](auto a){return a.right<=r.x+eps;});
        for(auto a:active)if(std::min(a.right,r.right)-std::max(a.x,r.x)>eps &&
                            std::min(a.top,r.top)-std::max(a.y,r.y)>eps)
            throw std::runtime_error("Packing collision");
        active.push_back(r);
    }
}
}
