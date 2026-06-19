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

int find_best_category(float *v, float *c, float *l, float mlv, float mcv, int nv, int ncl){
  float best_value = mcv;
  int image_index = -1;

  for(int i = 0; i < ncl; i++){
    float *current_leader = &l[i * nv];
    float *current_centroid = &c[i * nv];


    float leader_value = calculate_similarity(v, current_leader, nv);
    if(leader_value > mlv){
      float mean_value = calculate_similarity(v, current_centroid, nv);
      if(mean_value > best_value){
        best_value = mean_value;
        image_index = i;

      }
    }
  }
  return image_index;
}