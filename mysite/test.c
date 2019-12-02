#inlcude <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int a, b, n;
    
    scanf("%d %d", &a, &b);
    int n = add(a, b);
    
    printf("%d", n);
    
    return 0;
}
