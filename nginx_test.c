/*  gcc -DNGX_DEBUG=0 -g -o test test.c src/core/ngx_regex.c src/core/ngx_array.c src/core/ngx_list.c src/core/ngx_string.c  src/core/ngx_palloc.c  src/os/unix/ngx_alloc.c  -I src/os/unix/ -I src/core/ -I objs/ -lpcre
 */
#include <stdio.h>
#include "ngx_config.h"
#include "ngx_conf_file.h"
#include "nginx.h"
#include "ngx_core.h"
#include "ngx_string.h"
#include "ngx_palloc.h"
#include "ngx_array.h"
#include "ngx_regex.h"

/* required */ 
volatile ngx_cycle_t  *ngx_cycle;
 
/* NGX_DEBUG=0 */
void ngx_log_error_core(ngx_uint_t level, ngx_log_t *log, ngx_err_t err,
            const char *fmt, ...)
{
}
/* stub for regex */
void ngx_cdecl ngx_conf_log_error(ngx_uint_t level, ngx_conf_t *cf, ngx_err_t err,
     const char *fmt, ...)
{
}
char *
ngx_conf_set_flag_slot(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
}
/* stub for regex */

void regex_test(ngx_pool_t *pool, ngx_str_t * regex_str, ngx_str_t *input_str) {
    int caseless = 0;
//#if (NGX_PCRE)
    ngx_regex_compile_t  rc;
    u_char               errstr[NGX_MAX_CONF_ERRSTR];

    ngx_memzero(&rc, sizeof(ngx_regex_compile_t));

    rc.pool = pool;
    rc.pattern = *regex_str;
    rc.err.len = NGX_MAX_CONF_ERRSTR;
    rc.err.data = errstr;

#if (NGX_HAVE_CASELESS_FILESYSTEM)
    rc.options = NGX_REGEX_CASELESS;
#else
    rc.options = caseless ? NGX_REGEX_CASELESS : 0;
#endif

    printf("re compiler success \n");
    ngx_int_t  n = ngx_regex_compile(&rc);
    if (n != 0) {
        printf("re compiler error \n");
        return ;
    }
    n = ngx_regex_exec(rc.regex, input_str, NULL, 0);
    if (n == NGX_REGEX_NO_MATCHED) {
        ngx_sprintf(errstr, "NOK: re [%V] not matched content [%V]\n", regex_str, input_str);
    } else {
        ngx_sprintf(errstr, "OK: re [%V] matched content [%V]\n", regex_str, input_str);
    } 
    printf(errstr);
} 
void dump_array(ngx_array_t* a)
{
    if (a)
    {
        printf("array = 0x%x\n", a);
        printf("  .elts = 0x%x\n", a->elts);
        printf("  .nelts = %d\n", a->nelts);
        printf("  .size = %d\n", a->size);
        printf("  .nalloc = %d\n", a->nalloc);
        printf("  .pool = 0x%x\n", a->pool);
 
        printf("elements: ");
        int *ptr = (int*)(a->elts);
        for (; ptr < (int*)(a->elts + a->nalloc * a->size); )
        {
            printf("%d  ", *ptr++);
        }
        printf("\n");
    }
}
 
int main()
{
    ngx_pool_t *pool;
    int i;
 
    printf("--------------------------------\n");
    printf("create a new pool:\n");
    printf("--------------------------------\n");
    pool = ngx_create_pool(1024, NULL);
 
    printf("--------------------------------\n");
    printf("alloc an array from the pool:\n");
    printf("--------------------------------\n");
    ngx_array_t *a = ngx_array_create(pool, 5, sizeof(int));
    for (i = 0; i < 5; i++)
    {
        int *ptr = ngx_array_push(a);
        *ptr = 2*i;
    }
    dump_array(a);
    ngx_array_destroy(a);
 
    printf("--------------------------------\n");
    printf("regex test:\n");
    printf("--------------------------------\n");
    ngx_str_t regex = ngx_string("^abc");
    ngx_str_t input_str = ngx_string("abcd efg");
    regex_test(pool, &regex, &input_str);
    ngx_str_set(&input_str, "xxabcd efg");
    regex_test(pool, &regex, &input_str);
 
    ngx_destroy_pool(pool);
    return 0;
}
