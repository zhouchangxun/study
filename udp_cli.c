/*
* ref: https://blog.csdn.net/mrpre/article/details/43451775
*
#include <stdio.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <string.h>
#include <errno.h>
unsigned char revc_buf[1024];
 
int main()
{
        int fd,ret,recv_len,size=1024;
        struct sockaddr_in server_addr,addr;
        int val = 1;
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
        server_addr.sin_port = htons(43211);

        fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if(fd < 0)
        {
                perror("socket fail ");
                return -1;
        }

        printf("socket sucess\n");
 
        //方法1
        #if 1
        setsockopt(fd, IPPROTO_IP, IP_RECVERR , &val,sizeof(int));
        if(sendto(fd, "nihao", strlen("nihao"), 0, (const struct sockaddr *)&(server_addr), sizeof(struct sockaddr_in))<0)
        {
                perror("sendto fail ");
                return -1;
        }
        printf("sendto sucess\n");
        recv_len = recvfrom(fd, revc_buf, sizeof(revc_buf), 0, (struct sockaddr *)&addr, (int *)&size);
        if (recv_len == -1)
        {
                printf("Recv error !: errno: %d\n", errno);
                perror("Recv error !");
        }
        //方法2
        #elif 0
        ret = connect(fd, (const struct sockaddr *) &(server_addr), sizeof (struct sockaddr_in));
        if(ret < 0)
        {
                printf("connect fail\n");
                return -1;
        }

        ret = send(fd, "ni hao", strlen("nihao"),0);
        if(ret < 0)
        {
                printf("write fail\n");
                return -1;
        }

        recv_len = recvfrom(fd, revc_buf, sizeof(revc_buf), 0, (struct sockaddr *)&addr, (int *)&size);
        if (recv_len == -1)
        {
                printf("Recv error !: errno: %d\n", errno);
                perror("Recv error !");
        }
 
        #endif
        close(fd);

        return 0;
  }
