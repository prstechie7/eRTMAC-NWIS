import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Maximize2, RotateCcw, Layers, Compass, Zap } from "lucide-react";

interface ThreeWellboreProps {
  currentDepthMd?: number;
  isAlertActive?: boolean;
}

export const ThreeWellboreCanvas: React.FC<ThreeWellboreProps> = ({
  currentDepthMd = 2413.5,
  isAlertActive = true,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [viewMode, setViewMode] = useState<"wellbore" | "orb" | "split">("wellbore");
  const [rotationSpeed, setRotationSpeed] = useState(0.005);
  const isInteracting = useRef(false);
  const prevMousePos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    // Dimensions
    const width = currentMount.clientWidth || 500;
    const height = currentMount.clientHeight || 420;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a101d); // Deep space slate navy
    scene.fog = new THREE.FogExp2(0x0a101d, 0.015);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(24, 18, 30);
    camera.lookAt(0, -4, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    currentMount.appendChild(renderer.domElement);

    // 2. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 2.0);
    dirLight.position.set(20, 40, 20);
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0x10b981, 3.5, 60);
    pointLight.position.set(0, -10, 0);
    scene.add(pointLight);

    const alertLight = new THREE.PointLight(0xf43f5e, isAlertActive ? 4.0 : 0.2, 40);
    alertLight.position.set(0, -14, 0);
    scene.add(alertLight);

    // Root Group for interactive rotation
    const rootGroup = new THREE.Group();
    scene.add(rootGroup);

    // -------------------------------------------------------------
    // 3. Stratigraphic Slices (3D Horizontal Geological Planes)
    // -------------------------------------------------------------
    const strataData = [
      { name: "Surface / Alluvium", y: 4, color: 0x94a3b8, opacity: 0.15 },
      { name: "Girujan Clay", y: 0, color: 0x3b82f6, opacity: 0.22 },
      { name: "Upper Tipam Sandstone (Hazard Zone)", y: -10, color: 0xf59e0b, opacity: 0.35, isHazard: true },
      { name: "Barail Coal-Shale", y: -18, color: 0x6366f1, opacity: 0.25 },
    ];

    strataData.forEach((stratum) => {
      const planeGeo = new THREE.CylinderGeometry(18, 18, 0.4, 32);
      const planeMat = new THREE.MeshStandardMaterial({
        color: stratum.color,
        transparent: true,
        opacity: stratum.opacity,
        roughness: 0.3,
        metalness: 0.2,
      });
      const planeMesh = new THREE.Mesh(planeGeo, planeMat);
      planeMesh.position.y = stratum.y;
      rootGroup.add(planeMesh);

      // Wireframe ring boundary
      const ringGeo = new THREE.RingGeometry(17.9, 18.1, 32);
      const ringMat = new THREE.MeshBasicMaterial({ color: stratum.color, side: THREE.DoubleSide });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2;
      ringMesh.position.y = stratum.y + 0.21;
      rootGroup.add(ringMesh);
    });

    // -------------------------------------------------------------
    // 4. Primary Active Wellbore (SYN-NHK-05 3D Trajectory Tube)
    // -------------------------------------------------------------
    const curvePoints = [
      new THREE.Vector3(0, 5, 0),
      new THREE.Vector3(0.5, 2, 0.2),
      new THREE.Vector3(1.8, -2, 1.0),
      new THREE.Vector3(3.2, -6, 2.5),
      new THREE.Vector3(4.5, -10, 4.2), // Approaching depleted sand top
      new THREE.Vector3(5.8, -14, 5.8), // Bit currently at 2,413.5m MD
    ];
    const curve = new THREE.CatmullRomCurve3(curvePoints);
    const tubeGeo = new THREE.TubeGeometry(curve, 64, 0.45, 16, false);

    // Trajectory shader/material
    const tubeMat = new THREE.MeshStandardMaterial({
      color: isAlertActive ? 0xf43f5e : 0x10b981,
      roughness: 0.2,
      metalness: 0.8,
      emissive: isAlertActive ? 0x9f1239 : 0x065f46,
      emissiveIntensity: 0.6,
    });
    const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
    rootGroup.add(tubeMesh);

    // Active Drill Bit at tip
    const bitGeo = new THREE.ConeGeometry(0.85, 1.8, 16);
    const bitMat = new THREE.MeshStandardMaterial({
      color: 0xfacc15,
      metalness: 0.9,
      roughness: 0.1,
      emissive: 0x854d0e,
      emissiveIntensity: 0.5,
    });
    const bitMesh = new THREE.Mesh(bitGeo, bitMat);
    bitMesh.position.copy(curvePoints[curvePoints.length - 1]);
    bitMesh.rotation.x = Math.PI;
    rootGroup.add(bitMesh);

    // Hazard Influx Halo
    const haloGeo = new THREE.SphereGeometry(2.5, 24, 24);
    const haloMat = new THREE.MeshBasicMaterial({
      color: isAlertActive ? 0xf43f5e : 0x10b981,
      transparent: true,
      opacity: 0.25,
      wireframe: true,
    });
    const haloMesh = new THREE.Mesh(haloGeo, haloMat);
    haloMesh.position.copy(bitMesh.position);
    rootGroup.add(haloMesh);

    // -------------------------------------------------------------
    // 5. Offset Wells (NHK-014, NHK-019, NHK-021) 3D Trajectories
    // -------------------------------------------------------------
    const offsetOffsets = [
      { name: "NHK-014", dx: -6, dz: -5, color: 0xf43f5e },
      { name: "NHK-019", dx: 8, dz: -4, color: 0x38bdf8 },
      { name: "NHK-021", dx: -7, dz: 6, color: 0xa855f7 },
    ];

    offsetOffsets.forEach((off) => {
      const offCurvePoints = curvePoints.map((pt) => new THREE.Vector3(pt.x + off.dx, pt.y, pt.z + off.dz));
      const offCurve = new THREE.CatmullRomCurve3(offCurvePoints);
      const offTubeGeo = new THREE.TubeGeometry(offCurve, 32, 0.22, 8, false);
      const offTubeMat = new THREE.MeshBasicMaterial({ color: off.color, transparent: true, opacity: 0.65 });
      const offTubeMesh = new THREE.Mesh(offTubeGeo, offTubeMat);
      rootGroup.add(offTubeMesh);
    });

    // -------------------------------------------------------------
    // 6. Holographic 3D Floating AI Orb (Shopeers Style)
    // -------------------------------------------------------------
    const orbGroup = new THREE.Group();
    orbGroup.position.set(-10, 8, 12);
    scene.add(orbGroup);

    // Inner iridescent sphere
    const orbGeo = new THREE.SphereGeometry(2.4, 32, 32);
    const orbMat = new THREE.MeshPhysicalMaterial({
      color: 0x6366f1,
      emissive: 0x312e81,
      emissiveIntensity: 0.8,
      roughness: 0.1,
      metalness: 0.1,
      transmission: 0.6,
      ior: 1.5,
    });
    const orbMesh = new THREE.Mesh(orbGeo, orbMat);
    orbGroup.add(orbMesh);

    // Outer orbiting glowing rings
    const ring1Geo = new THREE.TorusGeometry(3.2, 0.08, 16, 64);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.8 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    orbGroup.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(3.8, 0.06, 16, 64);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.6 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 3;
    orbGroup.add(ring2);

    // -------------------------------------------------------------
    // Mouse Interaction
    // -------------------------------------------------------------
    const handleMouseDown = (e: MouseEvent) => {
      isInteracting.current = true;
      prevMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isInteracting.current) return;
      const dx = e.clientX - prevMousePos.current.x;
      const dy = e.clientY - prevMousePos.current.y;
      rootGroup.rotation.y += dx * 0.008;
      rootGroup.rotation.x += dy * 0.008;
      prevMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
      isInteracting.current = false;
    };

    currentMount.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    // -------------------------------------------------------------
    // Animation Loop
    // -------------------------------------------------------------
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Gentle auto rotation
      if (!isInteracting.current) {
        rootGroup.rotation.y += rotationSpeed;
      }

      // Bit drilling rotation & halo pulsing
      bitMesh.rotation.y += 0.08;
      const pulseScale = 1.0 + Math.sin(elapsed * 4.0) * 0.18;
      haloMesh.scale.set(pulseScale, pulseScale, pulseScale);

      // 3D AI Orb float & ring orbits
      orbGroup.position.y = 8 + Math.sin(elapsed * 2.0) * 0.6;
      ring1.rotation.z += 0.02;
      ring2.rotation.y += 0.015;

      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      currentMount.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("resize", handleResize);
      if (currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [isAlertActive, rotationSpeed]);

  return (
    <div className="relative w-full h-full min-h-[380px] rounded-3xl overflow-hidden shadow-card border border-slate-800/80 bg-[#0A101D]">
      {/* 3D WebGL Canvas Mount */}
      <div ref={mountRef} className="w-full h-full min-h-[380px] cursor-grab active:cursor-grabbing" />

      {/* Top Floating Controls */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-700/60 pointer-events-auto">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-[11px] font-mono font-bold text-white tracking-wider">
            THREE.JS 3D WELLBORE · 2,413.5m MD
          </span>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md p-1 rounded-full border border-slate-700/60 pointer-events-auto text-xs text-white">
          <button
            onClick={() => setRotationSpeed((p) => (p > 0 ? 0 : 0.005))}
            className="p-1.5 hover:bg-white/10 rounded-full transition-all"
            title="Toggle Auto Rotation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] font-mono px-2 text-slate-300">Orbit Active</span>
        </div>
      </div>

      {/* Bottom Floating Geological Legend */}
      <div className="absolute bottom-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 pointer-events-auto text-[10px] font-mono">
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400" /> Active Bit (SYN-NHK-05)
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1 text-rose-400">
            <span className="w-2 h-2 rounded-full bg-rose-500" /> Offset NHK-014 (38.5h NPT)
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1 text-amber-400">
            <span className="w-2 h-2 rounded-full bg-amber-400" /> Upper Tipam Sand Top
          </span>
        </div>

        <div className="bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-700/60 pointer-events-auto text-[10px] font-mono text-slate-400">
          Drag mouse to rotate 3D view
        </div>
      </div>
    </div>
  );
};
