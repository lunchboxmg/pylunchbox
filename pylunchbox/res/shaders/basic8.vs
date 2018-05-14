#version 400 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv;
layout(location = 2) in vec3 normal;

out vec2 pass_uv;
out vec3 pass_color;
out vec3 surf_normal;
out vec3 to_light;

uniform mat4 model;
uniform mat4 proj;
uniform mat4 view;

vec3 pos_light = vec3(10.0f, 10.0f, 10.0f);

void main(void) {

    vec4 pos_world = model * vec4(position, 1.0f);
    gl_Position = proj * view * pos_world;
    
    //mat3 mat_normal = transpose(inverse(mat3(model)));
    //surf_normal = mat_normal * normal;
    surf_normal = (model * vec4(normal, 1.0f)).xyz;
    to_light = pos_light - pos_world.xyz;

    pass_uv = uv;
    pass_color = vec3(1.0f, 1.0f, 1.0f);

}