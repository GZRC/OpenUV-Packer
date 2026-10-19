// SPDX-License-Identifier: GPL-3.0-or-later
#include "openuv.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
void require(bool ok){if(!ok)throw std::runtime_error("native test failed");}
int main(){try{
 std::mt19937 rng(42);std::uniform_real_distribution<double>d(.001,10);
 for(int n:{1,10,100,1000})for(bool rot:{false,true}){
  std::vector<openuv::Box>b;for(int i=0;i<n;++i)b.push_back({d(rng),d(rng)});
  for(int strategy:{0,1}){
   auto r=openuv::solve(b,.001,rot,strategy);require(r.scale>0 && r.p.size()==b.size());
   for(int i=0;i<n;++i){auto p=r.p[i];auto v=b[i];if(p.rotate)std::swap(v.w,v.h);
    require(rot || !p.rotate);
    require(p.x>=.001-1e-9 && p.y>=.001-1e-9 && p.x+v.w*r.scale<=.999+1e-9 && p.y+v.h*r.scale<=.999+1e-9);
    for(int j=0;j<i;++j){auto q=r.p[j];auto u=b[j];if(q.rotate)std::swap(u.w,u.h);
     require(p.x+v.w*r.scale+.002<=q.x+1e-9 || q.x+u.w*r.scale+.002<=p.x+1e-9 || p.y+v.h*r.scale+.002<=q.y+1e-9 || q.y+u.h*r.scale+.002<=p.y+1e-9);
    }
   }
  }
 }
 for(auto b:std::vector<std::vector<openuv::Box>>{{},{{0,1}},{{std::numeric_limits<double>::quiet_NaN(),1}}}){
  bool rejected=false;try{openuv::solve(b,.002,true,0);}catch(const std::exception&){rejected=true;}require(rejected);
 }
 std::cout<<"OpenUVCore geometry and rejection tests passed\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
