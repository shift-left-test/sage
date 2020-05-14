#include <stddef.h>

struct fred_t {
    int x;
};

void f1(struct fred_t *p)
{
    // dereference p and then check if it's NULL
    int x = p->x;
    if (p)
        printf("%d", x);
}

void f2()
{
    char str[10];

    const char *p = NULL;
    for (int i = 0; str[i] != '\0'; i++)
    {
        if (str[i] == ' ')
        {
            p = str + i;
            break;
        }
    }

    // p is NULL if str doesn't have a space. If str always has a
    // a space then the condition (str[i] != '\0') would be redundant
    return p[1];
}

void f3(int a)
{
    struct fred_t * fred1;
    struct fred_t *p = NULL;
    if (a == 1)
        p = fred1;

    // if a is not 1 then p is NULL
    p->x = 0;
}