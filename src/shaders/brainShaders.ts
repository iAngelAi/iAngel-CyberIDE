/**
 * Custom Shaders for the Neural Brain
 * 
 * These shaders create advanced visual effects for the brain core:
 * - Fresnel glow (rim lighting)
 * - Neural pulse effects
 * - Energy flow animations
 */

export const brainVertexShader = `
  varying vec3 vNormal;
  varying vec3 vViewPosition;
  varying vec2 vUv;
  
  uniform float time;
  uniform float pulseIntensity;
  
  void main() {
    vNormal = normalize(normalMatrix * normal);
    vUv = uv;
    
    // Add subtle vertex displacement for "breathing" effect
    vec3 newPosition = position;
    float displacement = sin(position.x * 2.0 + time) * 
                         sin(position.y * 2.0 + time) * 
                         sin(position.z * 2.0 + time) * 
                         0.05 * pulseIntensity;
    newPosition += normal * displacement;
    
    vec4 mvPosition = modelViewMatrix * vec4(newPosition, 1.0);
    vViewPosition = -mvPosition.xyz;
    gl_Position = projectionMatrix * mvPosition;
  }
`;

export const brainFragmentShader = `
  uniform float time;
  uniform float illuminationLevel;
  uniform vec3 primaryColor;
  uniform vec3 accentColor;
  
  varying vec3 vNormal;
  varying vec3 vViewPosition;
  varying vec2 vUv;
  
  void main() {
    // Calculate fresnel effect (rim glow)
    vec3 viewDirection = normalize(vViewPosition);
    float fresnel = pow(1.0 - abs(dot(viewDirection, vNormal)), 3.0);
    
    // Animated energy flow pattern
    float pattern = sin(vViewPosition.x * 3.0 + time) * 
                    sin(vViewPosition.y * 3.0 + time * 0.7) * 
                    sin(vViewPosition.z * 3.0 + time * 0.5);
    pattern = (pattern + 1.0) * 0.5; // Normalize to 0-1
    
    // Mix colors based on illumination and pattern
    vec3 baseColor = mix(primaryColor * 0.2, primaryColor, illuminationLevel);
    vec3 energyColor = mix(primaryColor, accentColor, pattern * illuminationLevel);
    
    // Combine effects
    vec3 finalColor = mix(baseColor, energyColor, fresnel * 0.7);
    
    // Add pulsing glow
    float pulse = sin(time * 2.0) * 0.5 + 0.5;
    finalColor += accentColor * fresnel * illuminationLevel * pulse * 0.3;
    
    gl_FragColor = vec4(finalColor, 0.85 + fresnel * 0.15);
  }
`;

export const neuralPathwayVertexShader = `
  varying vec2 vUv;
  
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

export const neuralPathwayFragmentShader = `
  uniform float time;
  uniform float flowSpeed;
  uniform vec3 pathwayColor;
  uniform float intensity;
  
  varying vec2 vUv;
  
  void main() {
    // Create flowing energy effect along the pathway
    float flow = fract(vUv.x + time * flowSpeed);
    float pulse = sin(flow * 3.14159 * 2.0);
    pulse = pow(pulse, 4.0) * 0.5 + 0.5;
    
    // Fade out at ends
    float fadeIn = smoothstep(0.0, 0.1, vUv.x);
    float fadeOut = smoothstep(1.0, 0.9, vUv.x);
    float alpha = pulse * intensity * fadeIn * fadeOut;
    
    vec3 glowColor = pathwayColor * (1.0 + pulse * 0.5);
    
    gl_FragColor = vec4(glowColor, alpha);
  }
`;
