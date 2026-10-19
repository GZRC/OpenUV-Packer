// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 OpenUV Packer contributors
#include <algorithm>
#include <cmath>
#include <future>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include <sstream>
#include "openuv.hpp"
using namespace openuv;
int main(int argc,char**argv){try{
 if(argc>1 && std::string(argv[1])=="--version"){std::cout<<"OpenUV Engine 0.2.0\n";return 0;}
 if(argc>1 && std::string(argv[1])=="--self-test"){
  auto r=solve({{1,1},{1,1}},.01,true,0);
  if(!(r.scale>0 && r.p.size()==2 && (r.p[1].y>r.p[0].y || r.p[1].x>r.p[0].x)))return 1;
  std::cout<<"native self-test passed\n";return 0;
 }
 size_t n;double margin;int rotate,workers,quality=1;
 std::string header;std::getline(std::cin,header);std::istringstream input(header);
 if(!(input>>n>>margin>>rotate>>workers)||n==0||n>100000||!std::isfinite(margin)||margin<0||margin>=.5||rotate<0||rotate>1||workers<1)throw std::runtime_error("Invalid header");
 input>>std::ws;if(!input.eof() && !(input>>quality))throw std::runtime_error("Invalid quality");
 std::vector<Box>b(n);for(auto&v:b)if(!(std::cin>>v.w>>v.h)||!std::isfinite(v.w)||!std::isfinite(v.h)||v.w<=0||v.h<=0)throw std::runtime_error("Invalid box");
 Result r;
 if(argc>1 && std::string(argv[1])=="--shelf") {
   r=solve(b,margin,rotate,0);auto other=solve(b,margin,rotate,1);
   if(other.scale>r.scale)r=other;r.searches=2;validate_result(b,margin,r);
 } else r=solve_best(b,margin,rotate,workers,quality);
 std::cerr<<"OPENUV "<<r.algorithm<<' '<<r.searches<<' '<<r.maxrects_skipped<<'\n';
 std::cout<<std::setprecision(17)<<r.scale<<'\n';for(auto p:r.p)std::cout<<p.x<<' '<<p.y<<' '<<p.rotate<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
