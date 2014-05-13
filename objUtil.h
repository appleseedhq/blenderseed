#include <stdio.h>
#include <string.h>
#include <math.h>

void objWriter (const char*, const char*, const char*, const char*, const char*, const char*);

// Function definition for objWriter
void objWriter (const char *header, const char *verts, const char *vn, const char *vt, const char *faces, const char *filepath) {
    FILE *fp;
    fp = fopen( filepath, "w");
    fprintf(fp, header);
    fprintf(fp, verts);
    fprintf(fp, vn);
    fprintf(fp, vt);
    fprintf(fp, faces);
    fclose(fp);     
}

