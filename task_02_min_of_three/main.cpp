
#include <iostream>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    long long a,b,c;
    if (!(std::cin >> a >> b >> c)) return 0;
    
    long long min = a;
    if (b < min) min = b;
    if (c < min) min = c;
    
    std::cout << min << std::endl;
    return 0;
}
