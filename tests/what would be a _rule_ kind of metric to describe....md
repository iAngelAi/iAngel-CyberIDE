# **CyberIDE Test Generation Standards**

Target Architecture: React \+ TypeScript \+ Vite \+ Three.js \+ Zod  
Strictness Level: High (No any, No unchecked mocks)

## **🛡️ Rule 1: The Data Integrity Contract**

**Constraint:** All mock data used in tests MUST pass the Zod validation defined in src/schemas/websocketValidation.ts.

* \[ \] **FAIL:** Manually writing { type: 'test\_result', passed: 5 } (Missing required fields).  
* \[ \] **PASS:** Using a helper that adheres to BackendWebSocketMessage.  
* \[ \] **VERIFICATION:** If BackendWebSocketMessageSchema.safeParse(mock) returns success: false, the test code is rejected.

## **🧪 Rule 2: The Logic Isolation Protocol**

**Constraint:** Business logic tests must not import three or react-three-fiber.

* \[ \] **FAIL:** Testing NeuralBrain.tsx to check if illumination calculation works.  
* \[ \] **PASS:** Testing brainHelpers.ts or useBrainState hook directly.  
* \[ \] **REASON:** Keep unit tests fast (\<10ms). 3D rendering mocks are notoriously flaky.

## **🔌 Rule 3: The Disconnect/Reconnect Simulation**

**Constraint:** useWebSocket tests must verify the "limbo" states.

* \[ \] **REQUIREMENT:** You must write a test case where the WebSocket closes (event code 1006\) and verifies that:  
  1. The status state updates to 'disconnected' or 'offline'.  
  2. The reconnectTimeoutRef is triggered (mock the timer).  
  3. No "send" operations throw errors during the disconnected state.

## **🔍 Rule 4: The Union Exhaustiveness Check**

**Constraint:** If a type is a Union (e.g., HealthStatus), all variants must be tested.

* \[ \] **Scope:** src/types/index.ts \-\> HealthStatus ('offline' | 'critical' | 'warning' | 'healthy' | 'optimal')  
* \[ \] **REQUIREMENT:** Ensure getStatusColor or equivalent UI renderers produce the correct output for ALL 5 variants.