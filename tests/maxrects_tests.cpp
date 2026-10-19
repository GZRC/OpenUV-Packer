// SPDX-License-Identifier: GPL-3.0-or-later
#include "openuv.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <stdexcept>
using namespace openuv;
void require(bool value){if(!value)throw std::runtime_error("MaxRects test failed");}
// Independent pairwise oracle, separate from the engine's sweep validator.
void verify(const std::vector<Box>& boxes,double margin,bool rotation,const Result& r) {
    require(r.scale>0 && std::isfinite(r.scale) && r.p.size()==boxes.size());
    for(size_t i=0;i<boxes.size();++i) {
        auto a=r.p[i];auto u=boxes[i];require(rotation || !a.rotate);if(a.rotate)std::swap(u.w,u.h);
        double right=a.x+u.w*r.scale,top=a.y+u.h*r.scale;
        require(a.x>=margin-1e-9 && a.y>=margin-1e-9 && right<=1-margin+1e-9 && top<=1-margin+1e-9);
        for(size_t j=0;j<i;++j) {
            auto b=r.p[j];auto v=boxes[j];if(b.rotate)std::swap(v.w,v.h);
            require(right+2*margin<=b.x+1e-9 || b.x+v.w*r.scale+2*margin<=a.x+1e-9 ||
                    top+2*margin<=b.y+1e-9 || b.y+v.h*r.scale+2*margin<=a.y+1e-9);
        }
    }
}
int main(){try{
    // Analytically known optima and rotation contract.
    for(bool rot:{false,true}) {
        auto r=solve_best({{2,1},{1,2}},0,rot,2,2);
        require(std::abs(r.scale-(rot?.5:1./3))<1e-7);
        verify({{2,1},{1,2}},0,rot,r);
    }
    auto squares=solve_best(std::vector<Box>(4,{1,1}),.01,true,2,1);
    require(std::abs(squares.scale-.48)<1e-7);
    std::mt19937 random(281);std::uniform_real_distribution<double>size(.005,2);
    int improved=0;
    for(int seed=0;seed<12;++seed)for(bool rotate:{false,true}) {
        std::vector<Box> boxes;for(int i=0;i<20+seed;++i)boxes.push_back({size(random),size(random)});
        for(double margin:{0.,.003}) {
            auto a=solve(boxes,margin,rotate,0),b=solve(boxes,margin,rotate,1);
            double baseline=std::max(a.scale,b.scale);
            for(int quality:{0,1,2}) {
                auto r=solve_best(boxes,margin,rotate,2,quality);
                verify(boxes,margin,rotate,r);require(r.scale>=baseline);
                if(r.scale>baseline*1.01)++improved;
                auto serial=solve_best(boxes,margin,rotate,1,quality);
                require(serial.scale==r.scale && serial.algorithm==r.algorithm);
                for(size_t i=0;i<r.p.size();++i)
                    require(serial.p[i].x==r.p[i].x && serial.p[i].y==r.p[i].y && serial.p[i].rotate==r.p[i].rotate);
            }
        }
    }
    require(improved>0);
    auto thin=std::vector<Box>{{.001,100},{100,.001},{.02,.3},{.3,.02},{1,1}};
    for(int quality:{0,1,2})verify(thin,.002,true,solve_best(thin,.002,true,2,quality));
    for(int quality:{0,1,2}) {
        const int limit=quality==0?128:quality==1?256:512;
        auto boundary=solve_best(std::vector<Box>(limit,{1,1}),.0001,true,2,quality);
        require(!boundary.maxrects_skipped && boundary.searches==4+2*quality);
        verify(std::vector<Box>(limit,{1,1}),.0001,true,boundary);
        auto r=solve_best(std::vector<Box>(513,{1,1}),.0001,true,2,quality);
        require(r.maxrects_skipped && r.searches==2);verify(std::vector<Box>(513,{1,1}),.0001,true,r);
    }
    bool rejected=false;
    try{solve_best(std::vector<Box>(10,{1,1}),.25,true,2,1);}catch(const std::exception&){rejected=true;}
    require(rejected);
    // Catch intentionally overlapping data via the production validator.
    rejected=false;Result overlap;overlap.scale=.5;overlap.p={{0,0,0},{0,0,0}};
    try{validate_result({{1,1},{1,1}},0,overlap);}catch(const std::exception&){rejected=true;}
    require(rejected);
    std::cout<<"MaxRects: exact optima, rotations, margins, baseline floor, determinism, fallback and collisions passed\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
