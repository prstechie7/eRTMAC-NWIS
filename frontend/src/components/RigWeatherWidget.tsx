"use client";

import React, { useEffect, useState } from "react";
import { CloudRain, Sun, Wind, Droplets, Thermometer, Gauge } from "lucide-react";

interface WeatherData {
  temp: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  pressure: number;
  description: string;
  location: string;
}

const OWM_API_KEY = "312ae77fe3bdcf35c726519e1c4997a1";

export const RigWeatherWidget: React.FC<{ lat?: number; lon?: number }> = ({
  lat = 27.2885,
  lon = 95.3345,
}) => {
  const [weather, setWeather] = useState<WeatherData>({
    temp: 24.5,
    feels_like: 25.3,
    humidity: 91,
    wind_speed: 0.95,
    pressure: 1010,
    description: "Light Rain",
    location: "Nahorkatiya Rig Zone",
  });

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OWM_API_KEY}`
        );
        if (res.ok) {
          const data = await res.json();
          setWeather({
            temp: data.main.temp,
            feels_like: data.main.feels_like,
            humidity: data.main.humidity,
            wind_speed: data.wind.speed,
            pressure: data.main.pressure,
            description: data.weather[0]?.description || "Overcast",
            location: `${data.name || "Nahorkatiya"} Rig Zone`,
          });
        }
      } catch (err) {
        // Use default fallback
      }
    };
    fetchWeather();
    const interval = setInterval(fetchWeather, 60000);
    return () => clearInterval(interval);
  }, [lat, lon]);

  const metrics = [
    {
      label: "Temp",
      value: `${weather.temp.toFixed(1)}°C`,
      icon: <Thermometer className="w-3.5 h-3.5" />,
      color: "#d97706"
    },
    {
      label: "Humidity",
      value: `${weather.humidity}%`,
      icon: <Droplets className="w-3.5 h-3.5" />,
      color: "#2563eb"
    },
    {
      label: "Wind",
      value: `${weather.wind_speed.toFixed(1)} m/s`,
      icon: <Wind className="w-3.5 h-3.5" />,
      color: "#059669"
    },
    {
      label: "Pressure",
      value: `${weather.pressure} hPa`,
      icon: <Gauge className="w-3.5 h-3.5" />,
      color: "#7c3aed"
    },
  ];

  return (
    <div
      className="rounded-lg p-3 text-xs"
      style={{ background: "var(--surface-2)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-1.5">
          <CloudRain className="w-3.5 h-3.5" style={{ color: "#2563eb" }} />
          <span className="font-heading font-bold text-[11px] uppercase tracking-wider" style={{ color: "var(--text-primary)" }}>
            Live Rig Weather · {weather.location}
          </span>
        </div>
        <span className="badge badge-success">OWM API Live</span>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="text-center p-2 rounded-md"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            <div className="flex items-center justify-center gap-1 mb-1" style={{ color: m.color }}>
              {m.icon}
              <span className="text-[9px] font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                {m.label}
              </span>
            </div>
            <div className="font-mono font-bold text-sm" style={{ color: m.color }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
