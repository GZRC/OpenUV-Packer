// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <vector>
namespace openuv {
struct Box { double w,h; };
struct Place { double x,y; int rotate; };
struct Result { double scale=0; std::vector<Place> p; };
Result solve(const std::vector<Box>& boxes,double margin,bool rotate,int strategy);
}
