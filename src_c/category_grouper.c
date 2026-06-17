#include <math.h>

float dot(float *v1,float *v2, int n){
  float product = 0.0f;
  for(int i=0; i < n; i++){
    product += v1[i]*v2[i];
  }
  return product;
}

float linalg_norm(float *v, int n){
  float norm = 0.0f;
  for(int i=0; i < n; i++){
    norm += v[i]*v[i];
  }
  return sqrtf(norm);
}

float calculate_similarity(float *v1, float *v2, int n){
  float dot_product = dot(v1, v2, n);
  float v1_norm = linalg_norm(v1, n);
  float v2_norm = linalg_norm(v2, n);
  if (v1_norm == 0.0f || v2_norm == 0.0f) return 0.0f;
  return dot_product / (v1_norm * v2_norm);
}
