#include  <sys/types.h>
#include  <sys/socket.h>
#include  <netinet/in.h>
#include  <string.h>
#include  <stdio.h>
#include  <arpa/inet.h>
#define MAXBUF 256
#define PUERTO 5000
#define GROUP "224.0.1.1"

int main(void) {

	int s;
	struct sockaddr_in srv;
	char buf[64];
	bzero(&srv, sizeof(srv));
	srv.sin_family = AF_INET;
	srv.sin_port = htons(PUERTO);
	if (inet_aton(GROUP, &srv.sin_addr) < 0) {
		perror("inet_aton");
		return 1;
	}

	if ((s = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		perror("socket");
		return 1;
	}

	printf("please input msg to send:\n");
	while (fgets(buf, MAXBUF, stdin)) {

		if (sendto(s, buf, strlen(buf), 0, (struct sockaddr *)&srv, sizeof(srv)) < 0) 
		{
			perror("recvfrom");

		} else {

			fprintf(stdout, "has sent to %s: %s ", GROUP, buf);

		}

	}

}
