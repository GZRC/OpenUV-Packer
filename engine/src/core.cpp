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
#include "openuv.hpp"
namespace openuv {
Result solve(const std::vector<Box>& b,double m,bool rot,int strategy) {
 if(b.empty() || b.size()>100000 || !std::isfinite(m) || m<0 || m>=.5)
  throw std::invalid_argument("Invalid packing input");
 for(auto v:b)if(!std::isfinite(v.w)||!std::isfinite(v.h)||v.w<=0||v.h<=0)
  throw std::invalid_argument("Invalid UV dimensions");
 std::vector<size_t> order(b.size()); std::iota(order.begin(),order.end(),0);
 std::stable_sort(order.begin(),order.end(),[&](auto a,auto c){
  auto score=[&](Box v){return strategy==0 ? v.w*v.h : std::max(v.w,v.h);};
  return score(b[a])>score(b[c]); });
 auto attempt=[&](double s,std::vector<Place>& p){
  double x=0,y=0,row=0; p.resize(b.size());
  for(auto i:order){ double w=b[i].w*s+2*m,h=b[i].h*s+2*m; int r=0;
   if(rot && h<w){std::swap(w,h);r=1;}
   if(x+w>1){x=0;y+=row;row=0;}
   if(w>1 || y+h>1)return false;
   p[i]={x+m,y+m,r};x+=w;row=std::max(row,h);
  }return true;
 };
 Result out; if(!attempt(0,out.p))throw std::runtime_error("Margins cannot fit all islands");
 double lo=0,hi=1; std::vector<Place> tmp;
 while(attempt(hi,tmp) && hi<1e12)hi*=2;
 for(int k=0;k<64;++k){double mid=(lo+hi)/2;if(attempt(mid,tmp))lo=mid;else hi=mid;}
 out.scale=lo*(1-1e-12);attempt(out.scale,out.p);return out;
}
}
