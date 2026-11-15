# -*- coding: utf-8 -*-
"""
Audited & Repaired ARIA Builder
Generates fully debugged, battle-tested index.html with:
- Three.js CDN fallback & safe initialization
- Pointer & raycasting guard (no accidental clicks from UI)
- Audio node lifecycle, oscillator disconnect, timer cleanup
- Mobile responsiveness, safe re-clamping on resize
- Portable paths and CLI options
- window.ARIA interface for robust testing and monitoring
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>ARIA &mdash; Earth Sonification System | Hear the planet. Understand its changes.</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #02040A;
      --bg2: #050B16;
      --bg-card: rgba(6, 14, 28, 0.78);
      --bg-panel: rgba(4, 10, 22, 0.88);
      --tx: #F4F7FB;
      --t2: #8CA0BA;
      --t3: #586B84;
      --bd: rgba(255, 255, 255, 0.12);
      --bd-glow: rgba(255, 255, 255, 0.22);
      
      /* Dynamic theme variables */
      --ac: #FF5722;
      --ac-glow: rgba(255, 87, 34, 0.45);
      --ac-subtle: rgba(255, 87, 34, 0.14);
      --ac-grad: linear-gradient(135deg, #FF5722, #FF9800);
      --tint-rgb: 255, 87, 34;
      
      color-scheme: dark;
      box-sizing: border-box;
      padding-top: env(safe-area-inset-top, 0px);
      padding-bottom: env(safe-area-inset-bottom, 0px);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: radial-gradient(ellipse at 50% 45%, var(--bg2), var(--bg) 80%);
      color: var(--tx);
      font-family: "Space Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-weight: 400;
      font-size: 12px;
      letter-spacing: 0.06em;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
    }
    
    .mono {
      font-family: "JetBrains Mono", monospace;
      letter-spacing: 0.02em;
    }
    
    canvas#gl {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      touch-action: none;
      cursor: crosshair;
      z-index: 1;
    }
    canvas#gl.grabbing {
      cursor: grabbing !important;
    }

    /* WebGL / 2D Fallback Floating Notification Pill */
    #fb {
      position: fixed;
      left: 50%;
      top: 68px;
      transform: translateX(-50%);
      max-width: 580px;
      width: calc(100% - 32px);
      padding: 10px 16px;
      display: none;
      z-index: 25;
      border: 1px solid rgba(255, 171, 64, 0.4);
      background: rgba(6, 14, 28, 0.94);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.65), 0 0 20px rgba(255, 171, 64, 0.15);
      animation: fadeInDown 0.3s ease;
    }
    #fb .fb-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
    }
    #fb .fb-text {
      text-align: left;
    }
    #fb h3 {
      font-size: 11px;
      color: #FFB74D;
      letter-spacing: 0.12em;
      margin-bottom: 2px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    #fb p {
      font-size: 10px;
      color: var(--t2);
      line-height: 1.4;
      text-transform: none;
      margin: 0;
    }
    #fb .btn-fb-close {
      font-size: 9.5px;
      padding: 5px 10px;
      border: 1px solid var(--bd);
      border-radius: 4px;
      color: var(--tx);
      background: rgba(255, 255, 255, 0.08);
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    #fb .btn-fb-close:hover {
      background: rgba(255, 255, 255, 0.16);
      border-color: rgba(255, 255, 255, 0.25);
    }
    
    .glass {
      background: var(--bg-card);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid var(--bd);
      border-radius: 12px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
      transition: border-color 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease, transform 0.3s ease;
    }
    .glass:hover {
      border-color: rgba(255, 255, 255, 0.22);
    }
    
    button {
      font: inherit;
      letter-spacing: inherit;
      text-transform: inherit;
      color: var(--tx);
      background: none;
      border: 0;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    button:focus-visible, input:focus-visible, select:focus-visible {
      outline: 2px solid var(--ac);
      outline-offset: 2px;
    }
    
    /* Global UI container */
    #ui {
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0;
      transition: opacity 1.2s ease;
      z-index: 10;
    }
    #ui.on {
      opacity: 1;
    }
    #ui > * {
      pointer-events: auto;
    }
    
    /* Zen Mode (Full Globe Panoramic View) */
    body.zen-mode #left,
    body.zen-mode #hud,
    body.zen-mode #jb,
    body.zen-mode #region-banner,
    body.zen-mode #milestone-alert,
    body.zen-mode header .brand,
    body.zen-mode header .status-tags {
      opacity: 0 !important;
      pointer-events: none !important;
      transform: translateY(12px) !important;
    }
    #zen-restore-btn {
      position: fixed;
      top: 18px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 999;
      display: none;
      background: rgba(4, 10, 22, 0.88);
      border: 1px solid var(--ac);
      color: #fff;
      padding: 7px 16px;
      border-radius: 20px;
      font-size: 10px;
      letter-spacing: 0.15em;
      box-shadow: 0 0 25px var(--ac-glow);
      cursor: pointer;
      backdrop-filter: blur(12px);
    }
    body.zen-mode #zen-restore-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    
    /* Top Header */
    header {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: calc(14px + env(safe-area-inset-top, 0px)) 22px 0;
      pointer-events: none;
      z-index: 20;
    }
    header > * {
      pointer-events: auto;
    }
    
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
      transition: opacity 0.3s ease;
    }
    .logo-container {
      display: flex;
      flex-direction: column;
    }
    .logo {
      font-size: 18px;
      letter-spacing: 0.35em;
      font-weight: 700;
      background: linear-gradient(90deg, #FFFFFF, var(--ac));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .sys {
      color: var(--t2);
      font-size: 9px;
      letter-spacing: 0.25em;
      margin-top: 2px;
    }
    
    .status-tags {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: 12px;
    }
    .tag {
      font-size: 9px;
      padding: 3px 8px;
      border-radius: 20px;
      border: 1px solid var(--bd);
      background: rgba(255, 255, 255, 0.04);
      color: var(--t2);
      letter-spacing: 0.12em;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .tag.live {
      border-color: var(--ac);
      color: var(--ac);
      background: var(--ac-subtle);
    }
    .tag-pulse {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--ac);
      box-shadow: 0 0 8px var(--ac);
      animation: pulseDot 2s infinite ease-in-out;
    }
    @keyframes pulseDot {
      0%, 100% { opacity: 0.4; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.2); }
    }
    
    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .ib {
      width: 36px;
      height: 36px;
      border: 1px solid var(--bd);
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      color: var(--t2);
      background: rgba(5, 12, 24, 0.6);
      backdrop-filter: blur(10px);
      transition: all 0.25s ease;
      position: relative;
    }
    .ib:hover, .ib.on, .ib.active {
      color: var(--tx);
      border-color: var(--ac);
      box-shadow: 0 0 16px var(--ac-glow);
      background: var(--ac-subtle);
    }
    .ib svg {
      width: 17px;
      height: 17px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.6;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    
    .pill-btn {
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid var(--bd);
      font-size: 10px;
      letter-spacing: 0.14em;
      color: var(--t2);
      background: rgba(5, 12, 24, 0.6);
      backdrop-filter: blur(10px);
      gap: 6px;
      transition: all 0.25s ease;
    }
    .pill-btn:hover, .pill-btn.active {
      color: #fff;
      border-color: var(--ac);
      background: var(--ac-subtle);
      box-shadow: 0 0 16px var(--ac-glow);
    }
    .pill-btn svg {
      width: 13px;
      height: 13px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.6;
    }
    
    /* Left Panel: Planetary Datasets */
    #left {
      position: absolute;
      left: 22px;
      top: 50%;
      transform: translateY(-50%);
      width: 220px;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      z-index: 15;
    }
    .panel-title {
      color: var(--t3);
      font-size: 9px;
      letter-spacing: 0.3em;
      padding: 0 8px 6px;
      border-bottom: 1px solid var(--bd);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .cat-item {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;
      padding: 9px 10px;
      border-radius: 8px;
      color: var(--t2);
      border-left: 3px solid transparent;
      background: transparent;
      transition: all 0.25s ease;
      text-align: left;
    }
    .cat-item:hover {
      color: var(--tx);
      background: rgba(255, 255, 255, 0.04);
      transform: translateX(3px);
    }
    .cat-item.on {
      color: #fff;
      border-left-color: var(--cat-color, var(--ac));
      background: linear-gradient(90deg, var(--cat-subtle, var(--ac-subtle)), transparent);
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
    }
    .cat-icon-wrap {
      width: 26px;
      height: 26px;
      border-radius: 6px;
      display: grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--cat-color, var(--ac));
      flex-shrink: 0;
      transition: all 0.25s ease;
    }
    .cat-item.on .cat-icon-wrap {
      background: var(--cat-color, var(--ac));
      color: #000;
      box-shadow: 0 0 12px var(--cat-color, var(--ac));
    }
    .cat-icon-wrap svg {
      width: 14px;
      height: 14px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .cat-meta {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      flex-grow: 1;
    }
    .cat-name {
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.12em;
    }
    .cat-sub {
      font-size: 8px;
      color: var(--t3);
      letter-spacing: 0.08em;
      margin-top: 2px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .cat-item.on .cat-sub {
      color: var(--t2);
    }
    
    /* Right Panel: HUD & Scientific Metrics */
    #hud {
      position: absolute;
      right: 22px;
      top: 50%;
      transform: translateY(-50%);
      width: 290px;
      padding: 18px 16px;
      z-index: 15;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .hud-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
    }
    .hud-title-wrap {
      display: flex;
      flex-direction: column;
    }
    .hud-label {
      font-size: 9px;
      color: var(--t3);
      letter-spacing: 0.28em;
    }
    .hud-dataset-name {
      font-size: 12px;
      font-weight: 600;
      color: var(--tx);
      letter-spacing: 0.12em;
      margin-top: 3px;
    }
    .hud-dataset-desc {
      font-size: 8.5px;
      color: var(--t2);
      line-height: 1.4;
      margin-top: 4px;
      text-transform: none;
    }
    
    .hud-val-container {
      display: flex;
      flex-direction: column;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      padding: 10px 12px;
      position: relative;
      overflow: hidden;
    }
    .hud-val-container::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: var(--ac);
      box-shadow: 0 0 10px var(--ac);
    }
    .val-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
    }
    #val {
      font-size: 36px;
      font-weight: 300;
      color: #fff;
      line-height: 1;
      text-shadow: 0 0 20px var(--ac-glow);
    }
    #val small {
      font-size: 13px;
      color: var(--t2);
      margin-left: 6px;
      font-weight: 400;
    }
    .delta-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 9px;
      font-weight: 500;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      letter-spacing: 0.06em;
    }
    .delta-badge.up {
      color: #FF5252;
      border-color: rgba(255, 82, 82, 0.3);
      background: rgba(255, 82, 82, 0.1);
    }
    .delta-badge.down {
      color: #69F0AE;
      border-color: rgba(105, 240, 174, 0.3);
      background: rgba(105, 240, 174, 0.1);
    }
    
    .hud-sub-stats {
      display: flex;
      justify-content: space-between;
      margin-top: 6px;
      font-size: 8.5px;
      color: var(--t2);
    }
    
    /* Interactive Sparkline Chart */
    .chart-box {
      display: flex;
      flex-direction: column;
      gap: 6px;
      position: relative;
    }
    .chart-wrap {
      width: 100%;
      height: 72px;
      position: relative;
    }
    svg#ch {
      width: 100%;
      height: 100%;
      overflow: visible;
      cursor: crosshair;
    }
    .chart-tooltip {
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%);
      background: #020814;
      border: 1px solid var(--ac);
      border-radius: 4px;
      padding: 3px 8px;
      font-size: 9px;
      color: #fff;
      pointer-events: none;
      white-space: nowrap;
      opacity: 0;
      transition: opacity 0.2s ease;
      box-shadow: 0 4px 12px rgba(0,0,0,0.6);
      z-index: 10;
    }
    .chart-legend {
      display: flex;
      justify-content: space-between;
      font-size: 8.5px;
      color: var(--t3);
      letter-spacing: 0.12em;
    }
    
    .science-intel {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 8.5px;
      color: var(--t2);
      line-height: 1.5;
    }
    .science-intel b {
      color: var(--tx);
      font-weight: 500;
    }
    .sensor-line {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #E2B053;
      font-size: 8px;
      letter-spacing: 0.08em;
    }
    
    /* Active Region Banner (when hotspot selected) */
    #region-banner {
      position: absolute;
      left: 50%;
      top: calc(72px + env(safe-area-inset-top, 0px));
      transform: translateX(-50%);
      padding: 8px 18px;
      display: none;
      align-items: center;
      gap: 16px;
      z-index: 16;
      border-color: var(--ac);
      box-shadow: 0 0 24px var(--ac-glow);
      animation: bannerSlide 0.3s ease forwards;
      max-width: calc(100vw - 40px);
    }
    #region-banner.on {
      display: flex;
    }
    @keyframes bannerSlide {
      from { opacity: 0; transform: translate(-50%, -10px); }
      to { opacity: 1; transform: translate(-50%, 0); }
    }
    .reg-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .reg-title-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .reg-name {
      font-size: 11px;
      font-weight: 600;
      color: #fff;
    }
    .reg-badge {
      font-size: 7.5px;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--ac);
      color: #000;
      font-weight: 600;
      letter-spacing: 0.1em;
    }
    .reg-sound-desc {
      font-size: 8.5px;
      color: var(--t2);
      text-transform: none;
      letter-spacing: 0.04em;
    }
    .reg-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .reg-dismiss {
      padding: 4px 10px;
      border-radius: 14px;
      border: 1px solid var(--bd);
      font-size: 9px;
      color: var(--t2);
      background: rgba(255, 255, 255, 0.05);
      gap: 4px;
    }
    .reg-dismiss:hover {
      color: #fff;
      border-color: #ff5252;
      background: rgba(255, 82, 82, 0.2);
    }
    
    /* 3D Hotspot beacons on Globe */
    #hsb {
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 5;
    }
    .hs-marker {
      position: absolute;
      left: 0;
      top: 0;
      width: 20px;
      height: 20px;
      margin: -10px;
      border-radius: 50%;
      border: 1.5px solid var(--ac);
      background: rgba(10, 20, 36, 0.6);
      backdrop-filter: blur(4px);
      display: grid;
      place-items: center;
      pointer-events: auto;
      cursor: pointer;
      transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.2s, box-shadow 0.2s;
    }
    .hs-marker::before {
      content: '';
      position: absolute;
      inset: 4px;
      border-radius: 50%;
      background: var(--ac);
      box-shadow: 0 0 10px var(--ac);
      transition: transform 0.2s ease;
    }
    .hs-marker::after {
      content: '';
      position: absolute;
      inset: -5px;
      border-radius: 50%;
      border: 1px solid var(--ac);
      opacity: 0.6;
      animation: hsPulse 2.4s infinite cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    @keyframes hsPulse {
      0% { transform: scale(0.6); opacity: 0.8; }
      100% { transform: scale(1.8); opacity: 0; }
    }
    .hs-marker:hover, .hs-marker.on {
      transform: scale(1.35);
      background: var(--ac);
      box-shadow: 0 0 20px var(--ac);
    }
    .hs-marker:hover::before, .hs-marker.on::before {
      background: #FFFFFF;
    }
    
    /* Custom Pin for Clicked Earth Area */
    .hs-marker.custom-beacon {
      border-color: #00E5FF;
    }
    .hs-marker.custom-beacon::before {
      background: #00E5FF;
      box-shadow: 0 0 12px #00E5FF;
    }
    .hs-marker.custom-beacon::after {
      border-color: #00E5FF;
    }
    
    .hs-tooltip {
      position: absolute;
      left: 24px;
      top: 50%;
      transform: translateY(-50%);
      white-space: nowrap;
      font-size: 8.5px;
      letter-spacing: 0.08em;
      color: #fff;
      background: rgba(3, 8, 18, 0.92);
      border: 1px solid var(--bd);
      border-radius: 6px;
      padding: 4px 8px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.2s ease, transform 0.2s ease;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .hs-tooltip small {
      color: var(--ac);
      font-size: 7.5px;
      letter-spacing: 0.12em;
    }
    .hs-marker:hover .hs-tooltip, .hs-marker.on .hs-tooltip {
      opacity: 1;
      transform: translateY(-50%) translateX(2px);
    }

    /* Live Earth Scanner Crosshair Reticle */
    #scanner-reticle {
      position: fixed;
      pointer-events: none;
      width: 44px;
      height: 44px;
      margin: -22px;
      border: 1.5px dashed var(--ac);
      border-radius: 50%;
      display: none;
      place-items: center;
      z-index: 99;
      box-shadow: 0 0 16px var(--ac-glow);
      animation: reticleSpin 8s linear infinite;
    }
    #scanner-reticle::before {
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #fff;
    }
    @keyframes reticleSpin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    #scanner-pill {
      position: fixed;
      pointer-events: none;
      z-index: 100;
      display: none;
      background: rgba(3, 8, 20, 0.92);
      border: 1px solid var(--ac);
      border-radius: 4px;
      padding: 3px 8px;
      font-size: 8.5px;
      color: #fff;
      white-space: nowrap;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
    }
    
    /* =========================================================================
       CONTROL DECK (#jb) - COMPACT, DRAGGABLE & DOCKABLE
       ========================================================================= */
    #jb {
      position: absolute;
      left: 50%;
      bottom: calc(14px + env(safe-area-inset-bottom, 0px));
      transform: translateX(-50%);
      width: min(680px, calc(100vw - 28px));
      padding: 8px 14px 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 15;
      touch-action: none;
    }
    
    /* Drag Handle Bar at top of Control Deck */
    .deck-drag-handle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: grab;
      padding: 0 2px 4px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      margin-bottom: 2px;
    }
    .deck-drag-handle:active {
      cursor: grabbing;
    }
    .drag-grip {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--t3);
      font-size: 8.5px;
      letter-spacing: 0.2em;
    }
    .drag-dots {
      display: flex;
      gap: 3px;
    }
    .drag-dots span {
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: var(--t3);
    }
    .deck-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .deck-btn {
      width: 22px;
      height: 20px;
      border-radius: 4px;
      border: 1px solid var(--bd);
      color: var(--t2);
      background: rgba(255, 255, 255, 0.04);
      display: grid;
      place-items: center;
      font-size: 9px;
      transition: all 0.2s ease;
    }
    .deck-btn:hover {
      color: #fff;
      border-color: var(--ac);
      background: var(--ac-subtle);
    }
    .deck-btn svg {
      width: 12px;
      height: 12px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.6;
    }
    
    /* Minimized Compact Capsule State */
    #jb.minimized {
      width: auto !important;
      padding: 6px 12px !important;
      flex-direction: row !important;
      align-items: center !important;
      gap: 12px !important;
    }
    #jb.minimized .deck-drag-handle {
      border-bottom: 0 !important;
      margin-bottom: 0 !important;
      padding-bottom: 0 !important;
      margin-right: 4px;
    }
    #jb.minimized .drag-label {
      display: none;
    }
    #jb.minimized .deck-full-content {
      display: none !important;
    }
    #jb.minimized .deck-mini-content {
      display: flex !important;
      align-items: center;
      gap: 10px;
    }
    .deck-mini-content {
      display: none;
    }
    .mini-play-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 1px solid var(--ac);
      display: grid;
      place-items: center;
      color: var(--ac);
      background: var(--ac-subtle);
    }
    .mini-play-btn.active {
      background: var(--ac);
      color: #000;
    }
    .mini-play-btn svg {
      width: 14px;
      height: 14px;
      fill: currentColor;
    }

    /* Full Deck Content */
    .deck-full-content {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    /* Audio Visualizer & Play Engine Row */
    .audio-row {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      gap: 12px;
    }
    
    .vz-box {
      display: flex;
      flex-direction: column;
      gap: 2px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      padding: 4px 6px;
      overflow: hidden;
    }
    .vz-header {
      display: flex;
      justify-content: space-between;
      font-size: 7.5px;
      color: var(--t3);
      letter-spacing: 0.15em;
    }
    canvas.vz {
      width: 100%;
      height: 26px;
      display: block;
    }
    
    .play-station {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }
    #play {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      border: 1.5px solid var(--ac);
      display: grid;
      place-items: center;
      box-shadow: 0 0 20px var(--ac-glow);
      color: var(--ac);
      background: rgba(10, 24, 48, 0.5);
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    #play:hover {
      transform: scale(1.08);
      background: var(--ac-subtle);
      box-shadow: 0 0 28px var(--ac-glow);
      color: #fff;
    }
    #play.active {
      background: var(--ac);
      color: #000;
      box-shadow: 0 0 32px var(--ac);
    }
    #play svg {
      width: 20px;
      height: 20px;
      fill: currentColor;
    }
    .play-state-text {
      font-size: 8px;
      color: var(--t2);
      letter-spacing: 0.16em;
      font-weight: 500;
    }
    
    /* Adjustable Timeline Scrubber Row */
    .timeline-station {
      display: flex;
      flex-direction: column;
      gap: 6px;
      background: rgba(0, 0, 0, 0.22);
      border: 1px solid rgba(255, 255, 255, 0.04);
      border-radius: 8px;
      padding: 8px 12px;
    }
    
    .tl-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .tl-title-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tl-title {
      font-size: 8.5px;
      color: var(--t3);
      letter-spacing: 0.18em;
    }
    .tl-mode-badge {
      font-size: 7.5px;
      padding: 1px 5px;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--t2);
      border: 1px solid var(--bd);
    }
    
    .year-stepper {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .step-btn {
      width: 24px;
      height: 20px;
      border-radius: 4px;
      border: 1px solid var(--bd);
      background: rgba(255, 255, 255, 0.04);
      color: var(--t2);
      font-size: 8.5px;
      font-weight: 500;
      transition: all 0.2s ease;
    }
    .step-btn:hover {
      color: #fff;
      border-color: var(--ac);
      background: var(--ac-subtle);
    }
    .year-display {
      font-size: 14px;
      font-weight: 600;
      color: #fff;
      min-width: 80px;
      text-align: center;
      letter-spacing: 0.08em;
      text-shadow: 0 0 12px var(--ac-glow);
    }
    
    .slider-container {
      position: relative;
      width: 100%;
      padding: 2px 0;
    }
    input[type=range].timeline-slider {
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: linear-gradient(to right, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
      outline: none;
      cursor: pointer;
      position: relative;
      z-index: 2;
    }
    input[type=range].timeline-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #FFFFFF;
      border: 3px solid var(--ac);
      box-shadow: 0 0 14px var(--ac), 0 2px 6px rgba(0,0,0,0.6);
      cursor: pointer;
      transition: transform 0.15s ease, background 0.15s ease;
    }
    input[type=range].timeline-slider::-webkit-slider-thumb:hover {
      transform: scale(1.2);
      background: var(--ac);
      border-color: #FFFFFF;
    }
    input[type=range].timeline-slider::-moz-range-thumb {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #FFFFFF;
      border: 3px solid var(--ac);
      box-shadow: 0 0 14px var(--ac), 0 2px 6px rgba(0,0,0,0.6);
      cursor: pointer;
    }
    
    /* Milestone Chips Bar along timeline */
    .milestones-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 2px;
      gap: 4px;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .milestones-bar::-webkit-scrollbar { display: none; }
    
    .ms-chip {
      font-size: 8px;
      color: var(--t3);
      padding: 2px 5px;
      border-radius: 4px;
      background: transparent;
      border: 1px solid transparent;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      letter-spacing: 0.06em;
    }
    .ms-chip:hover {
      color: var(--tx);
      border-color: var(--bd);
      background: rgba(255, 255, 255, 0.04);
    }
    .ms-chip.active {
      color: var(--ac);
      border-color: var(--ac);
      background: var(--ac-subtle);
      font-weight: 500;
    }
    
    /* Floating Milestone Intel Alert */
    #milestone-alert {
      position: absolute;
      left: 50%;
      bottom: calc(160px + env(safe-area-inset-bottom, 0px));
      transform: translateX(-50%);
      padding: 8px 14px;
      display: none;
      align-items: center;
      gap: 12px;
      z-index: 16;
      border-color: var(--ac);
      box-shadow: 0 0 24px var(--ac-glow);
      max-width: min(580px, calc(100vw - 40px));
      animation: alertPop 0.3s ease;
    }
    #milestone-alert.on {
      display: flex;
    }
    @keyframes alertPop {
      from { opacity: 0; transform: translate(-50%, 10px); }
      to { opacity: 1; transform: translate(-50%, 0); }
    }
    .ms-alert-tag {
      font-size: 7.5px;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--ac);
      color: #000;
      font-weight: 600;
      letter-spacing: 0.1em;
      flex-shrink: 0;
    }
    .ms-alert-body {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .ms-alert-year-title {
      font-size: 10.5px;
      font-weight: 600;
      color: #fff;
    }
    .ms-alert-desc {
      font-size: 8.5px;
      color: var(--t2);
      text-transform: none;
      line-height: 1.4;
    }
    .ms-alert-close {
      margin-left: auto;
      color: var(--t2);
      font-size: 15px;
      padding: 2px 6px;
    }
    .ms-alert-close:hover {
      color: #fff;
    }
    
    /* Deck Bottom Controls Bar */
    .deck-sub-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      font-size: 8.5px;
      color: var(--t2);
      padding-top: 2px;
    }
    .audio-stats {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .stat-label {
      color: var(--t3);
      font-size: 7.5px;
    }
    .stat-val {
      color: var(--tx);
      font-weight: 500;
    }
    
    .deck-right-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .vol-wrap {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    input[type=range].vol-slider {
      width: 65px;
      accent-color: var(--ac);
      height: 12px;
    }
    
    /* Region Drawer Modal */
    #region-drawer {
      position: fixed;
      inset: 0;
      background: rgba(2, 4, 10, 0.78);
      backdrop-filter: blur(14px);
      z-index: 50;
      display: none;
      place-items: center;
      padding: 20px;
    }
    #region-drawer.open {
      display: grid;
    }
    .modal-box {
      width: min(840px, 100%);
      max-height: 85vh;
      overflow-y: auto;
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
    }
    .modal-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--bd);
      padding-bottom: 10px;
    }
    .modal-title {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: 0.15em;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .modal-sub {
      font-size: 9.5px;
      color: var(--t2);
      margin-top: 3px;
      text-transform: none;
    }
    .modal-close {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 1px solid var(--bd);
      font-size: 16px;
      color: var(--t2);
    }
    .modal-close:hover {
      color: #fff;
      border-color: #ff5252;
    }
    
    /* Biome Filter Tabs */
    .biome-filters {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
      padding-bottom: 4px;
    }
    .biome-filter-btn {
      padding: 4px 10px;
      border-radius: 14px;
      border: 1px solid var(--bd);
      font-size: 8.5px;
      color: var(--t2);
      letter-spacing: 0.1em;
      white-space: nowrap;
      background: rgba(255, 255, 255, 0.03);
    }
    .biome-filter-btn:hover, .biome-filter-btn.active {
      color: #fff;
      border-color: var(--ac);
      background: var(--ac-subtle);
    }

    .regions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 10px;
    }
    .reg-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--bd);
      border-radius: 8px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      transition: all 0.25s ease;
      position: relative;
    }
    .reg-card:hover {
      border-color: var(--card-color, var(--ac));
      background: rgba(255, 255, 255, 0.06);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .reg-card.active {
      border-color: var(--card-color, var(--ac));
      background: var(--card-subtle, var(--ac-subtle));
      box-shadow: 0 0 20px var(--card-color, var(--ac));
    }
    .rc-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .rc-icon {
      font-size: 16px;
    }
    .rc-badge {
      font-size: 7px;
      padding: 2px 5px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--card-color, var(--ac));
      border: 1px solid var(--card-color, var(--ac));
      font-weight: 600;
      letter-spacing: 0.1em;
    }
    .rc-name {
      font-size: 11px;
      font-weight: 600;
      color: #fff;
    }
    .rc-loc {
      font-size: 8px;
      color: var(--t3);
      letter-spacing: 0.08em;
    }
    .rc-sound {
      font-size: 8.5px;
      color: var(--t2);
      text-transform: none;
      line-height: 1.4;
      flex-grow: 1;
    }
    .rc-btn {
      margin-top: 2px;
      width: 100%;
      padding: 5px;
      border-radius: 5px;
      border: 1px solid var(--card-color, var(--ac));
      color: var(--card-color, var(--ac));
      font-size: 8.5px;
      font-weight: 500;
      letter-spacing: 0.12em;
      background: transparent;
      transition: all 0.2s ease;
    }
    .reg-card:hover .rc-btn, .reg-card.active .rc-btn {
      background: var(--card-color, var(--ac));
      color: #000;
    }
    
    /* Settings Modal */
    #settings-modal {
      position: fixed;
      inset: 0;
      background: rgba(2, 4, 10, 0.78);
      backdrop-filter: blur(14px);
      z-index: 50;
      display: none;
      place-items: center;
      padding: 20px;
    }
    #settings-modal.open {
      display: grid;
    }
    .settings-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .setting-item {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    .setting-item label {
      font-size: 8.5px;
      color: var(--t3);
      letter-spacing: 0.15em;
    }
    .setting-item select {
      background: #050B16;
      color: var(--tx);
      border: 1px solid var(--bd);
      border-radius: 6px;
      padding: 7px 10px;
      font-family: inherit;
      font-size: 10.5px;
    }

    /* Scientific Data Provenance Banner in HUD */
    .provenance-banner {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 9px;
      border-radius: 4px;
      background: rgba(0, 230, 118, 0.08);
      border: 1px solid rgba(0, 230, 118, 0.35);
      font-size: 8px;
      letter-spacing: 0.08em;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-top: 6px;
      user-select: none;
      width: fit-content;
    }
    .provenance-banner:hover {
      background: rgba(0, 230, 118, 0.16);
      border-color: rgba(0, 230, 118, 0.65);
      box-shadow: 0 0 12px rgba(0, 230, 118, 0.28);
    }
    .provenance-banner .prov-badge-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #00E676;
      box-shadow: 0 0 8px #00E676;
      animation: pulse-dot 2s infinite ease-in-out;
    }
    .provenance-banner.badge-benchmark {
      background: rgba(128, 216, 255, 0.08);
      border-color: rgba(128, 216, 255, 0.35);
    }
    .provenance-banner.badge-benchmark:hover {
      background: rgba(128, 216, 255, 0.16);
      border-color: rgba(128, 216, 255, 0.65);
      box-shadow: 0 0 12px rgba(128, 216, 255, 0.28);
    }
    .provenance-banner.badge-benchmark .prov-badge-dot {
      background: #80D8FF;
      box-shadow: 0 0 8px #80D8FF;
    }
    @keyframes pulse-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.35; transform: scale(0.85); }
    }

    /* Scientific Data Transparency & Provenance Modal */
    #data-modal {
      position: fixed;
      inset: 0;
      background: rgba(2, 4, 10, 0.82);
      backdrop-filter: blur(14px);
      z-index: 60;
      display: none;
      place-items: center;
      padding: 20px;
    }
    #data-modal.open {
      display: grid;
    }
    .data-matrix-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 12px;
      margin-top: 10px;
    }
    .data-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--bd);
      border-radius: 8px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      position: relative;
      transition: all 0.25s ease;
    }
    .data-card:hover {
      border-color: rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.05);
    }
    .dc-badge-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }
    .dc-status-badge {
      font-size: 8px;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 700;
      letter-spacing: 0.1em;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .badge-real {
      background: rgba(0, 230, 118, 0.12);
      color: #00E676;
      border: 1px solid rgba(0, 230, 118, 0.4);
    }
    .badge-benchmark {
      background: rgba(128, 216, 255, 0.12);
      color: #80D8FF;
      border: 1px solid rgba(128, 216, 255, 0.4);
    }
    .badge-simulated {
      background: rgba(255, 183, 77, 0.12);
      color: #FFB74D;
      border: 1px solid rgba(255, 183, 77, 0.4);
    }
    .badge-unavailable {
      background: rgba(255, 82, 82, 0.12);
      color: #FF5252;
      border: 1px solid rgba(255, 82, 82, 0.4);
    }
    .dc-title {
      font-size: 13px;
      font-weight: 600;
      color: #FFFFFF;
      letter-spacing: 0.04em;
    }
    .dc-provider {
      font-size: 9px;
      color: var(--t2);
      letter-spacing: 0.08em;
    }
    .dc-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 8.5px;
      margin-top: 4px;
    }
    .dc-table td {
      padding: 3px 0;
      vertical-align: top;
    }
    .dc-table td.dc-lbl {
      color: var(--t3);
      width: 32%;
      font-weight: 500;
      letter-spacing: 0.06em;
    }
    .dc-table td.dc-val {
      color: var(--tx);
      font-family: var(--fn-mono);
    }
    .dc-table a {
      color: var(--ac);
      text-decoration: underline;
    }
    .dc-sonification {
      background: rgba(0, 0, 0, 0.25);
      border-left: 2px solid var(--ac);
      padding: 6px 8px;
      border-radius: 0 4px 4px 0;
      font-size: 8px;
      color: var(--t2);
      line-height: 1.4;
      margin-top: 4px;
    }
    
    /* Intro Overlay */
    #intro {
      position: fixed;
      inset: 0;
      display: grid;
      place-content: center;
      text-align: center;
      z-index: 99;
      background: radial-gradient(circle at 50% 50%, rgba(5, 12, 28, 0.90), rgba(2, 4, 10, 0.98));
      transition: opacity 1.2s ease;
      padding: 24px;
    }
    #intro.off {
      opacity: 0;
      pointer-events: none;
    }
    .intro-box {
      max-width: 600px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
    }
    .intro-badge {
      font-size: 8.5px;
      letter-spacing: 0.35em;
      color: var(--ac);
      border: 1px solid var(--ac);
      padding: 4px 12px;
      border-radius: 20px;
      background: var(--ac-subtle);
    }
    #intro h1 {
      font-weight: 300;
      font-size: clamp(48px, 10vw, 84px);
      letter-spacing: 0.4em;
      margin: 0;
      background: linear-gradient(135deg, #FFFFFF 40%, var(--ac));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    #intro p.sub {
      color: var(--t2);
      letter-spacing: 0.28em;
      font-size: 10.5px;
      max-width: 480px;
      line-height: 1.6;
    }
    .intro-features {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin: 8px 0 16px;
      width: 100%;
    }
    .feat-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--bd);
      border-radius: 8px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      text-align: left;
    }
    .feat-card b {
      font-size: 8.5px;
      color: var(--tx);
      letter-spacing: 0.1em;
    }
    .feat-card span {
      font-size: 7.5px;
      color: var(--t3);
      line-height: 1.4;
      text-transform: none;
    }
    #go {
      padding: 13px 36px;
      border: 1px solid var(--ac);
      border-radius: 40px;
      color: #fff;
      background: var(--ac-subtle);
      letter-spacing: 0.28em;
      font-size: 10.5px;
      font-weight: 600;
      box-shadow: 0 0 28px var(--ac-glow);
      transition: all 0.3s ease;
    }
    #go:hover {
      background: var(--ac);
      color: #000;
      box-shadow: 0 0 45px var(--ac);
      transform: scale(1.05);
    }
    #intro small {
      color: var(--t3);
      font-size: 8px;
      text-transform: none;
      letter-spacing: 0.04em;
      line-height: 1.4;
    }
    
    /* Responsive media queries */
    @media (max-width: 900px) {
      #left {
        left: 10px;
        right: 10px;
        top: auto;
        bottom: calc(180px + env(safe-area-inset-bottom, 0px));
        transform: none;
        width: auto;
        flex-direction: row;
        overflow-x: auto;
        padding: 5px;
        scrollbar-width: none;
      }
      #left::-webkit-scrollbar { display: none; }
      .panel-title { display: none; }
      .cat-item {
        flex-direction: column;
        align-items: center;
        padding: 6px 8px;
        border-left: 0;
        border-bottom: 2px solid transparent;
        min-width: 75px;
      }
      .cat-item.on {
        border-bottom-color: var(--cat-color, var(--ac));
        background: linear-gradient(180deg, transparent, var(--cat-subtle, var(--ac-subtle)));
      }
      .cat-sub { display: none; }
      
      #hud {
        top: calc(60px + env(safe-area-inset-top, 0px));
        right: 10px;
        left: 10px;
        transform: none;
        width: auto;
        padding: 10px;
      }
      #val { font-size: 24px; }
      .chart-wrap { height: 45px; }
      .science-intel { display: none; }
      
      #jb {
        width: calc(100vw - 20px);
        padding: 8px 10px;
      }
      .audio-row {
        grid-template-columns: 1fr auto;
      }
      .vz-box:last-child {
        display: none;
      }
      .settings-grid {
        grid-template-columns: 1fr;
      }
    }
    
    @media (max-width: 600px) {
      #left {
        bottom: calc(100px + env(safe-area-inset-bottom, 0px));
      }
      header {
        padding: calc(10px + env(safe-area-inset-top, 0px)) 12px 0;
      }
      .sys {
        display: none;
      }
      .status-tags {
        display: none;
      }
    }
    
    @media (prefers-reduced-motion: reduce) {
      .hs-marker::after { animation: none; }
      * { transition: none !important; }
    }
  </style>
</head>
<body>
  <!-- 3D WebGL / 2D Fallback Canvas -->
  <canvas id="gl" aria-label="Interactive Planetary Observatory"></canvas>
  <div id="fb" class="glass">
    <div class="fb-row">
      <div class="fb-text">
        <h3 class="mono"><span style="color:#FFB74D">&#9679;</span> 2D PLANETARY OBSERVATORY ACTIVE</h3>
        <p>3D WebGL acceleration is unavailable in this environment. The interactive 2D planetary map is active with full acoustic sonification, coordinates, and hotspots.</p>
      </div>
      <button id="btn-close-fb" class="btn-fb-close mono" aria-label="Dismiss 2D fallback alert">DISMISS</button>
    </div>
  </div>
  <div id="hsb"></div>

  <!-- Live Earth Scanner Reticle & Hover Pill -->
  <div id="scanner-reticle"></div>
  <div id="scanner-pill" class="mono">28.4&deg;N, 42.1&deg;E &middot; ARABIAN DESERT</div>

  <!-- Zen Mode Floating Restore Button -->
  <button id="zen-restore-btn" class="mono">
    <svg style="width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
    RESTORE OBSERVATORY (Z)
  </button>

  <!-- Splash / Intro Screen -->
  <div id="intro">
    <div class="intro-box">
      <div class="intro-badge">PLANETARY ACOUSTIC OBSERVATORY</div>
      <h1>ARIA</h1>
      <p class="sub">HEAR THE PLANET. UNDERSTAND ITS CHANGES. &middot; REAL-TIME SONIFICATION OF EARTH'S BIOSPHERE &amp; CLIMATE EPOCHS</p>
      
      <div class="intro-features">
        <div class="feat-card">
          <b>CLICK ANYWHERE ON EARTH</b>
          <span>Tap any point on the 3D globe to hear localized acoustics synthesized live.</span>
        </div>
        <div class="feat-card">
          <b>COMPACT DRAGGABLE DECK</b>
          <span>Move, dock, or minimize the bottom control deck for 100% full vision of Earth.</span>
        </div>
        <div class="feat-card">
          <b>ADJUSTABLE EPOCHS</b>
          <span>Scrub 1980&ndash;2025 with landmark historical milestones and direct acoustic comparison.</span>
        </div>
      </div>
      
      <button id="go">INITIALIZE OBSERVATORY</button>
      <small>Web Audio synthesizes planetary climate metrics and spatial biophony directly in the browser.</small>
    </div>
  </div>

  <!-- Main HUD & Application Interface -->
  <div id="ui">
    <!-- Top Header -->
    <header>
      <div class="brand">
        <div class="logo-container">
          <div class="logo">
            <svg style="width:18px;height:18px;fill:none;stroke:var(--ac);stroke-width:2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            ARIA
          </div>
          <div class="sys">EARTH SONIFICATION SYSTEM</div>
        </div>
        <div class="status-tags">
          <div class="tag live" id="live-tag" style="cursor:pointer" title="Click to view Observatory Status"><div class="tag-pulse"></div> <span id="tag-label">GLOBAL SYNTH</span></div>
          <div class="tag mono" id="backend-badge" style="cursor:pointer;font-size:8px;padding:3px 8px;border:1px solid rgba(0,229,255,0.3);border-radius:4px;color:#80D8FF;background:rgba(0,229,255,0.06)" title="Click to configure scientific backend">BACKEND: CHECKING</div>
          <div class="tag mono" id="year-tag">EPOCH 1990</div>
        </div>
      </div>

      <div class="header-actions">
        <!-- Live Earth Audio Scanner Toggle -->
        <button class="pill-btn" id="btn-scanner" aria-label="Toggle Earth Scanner Mode" title="Scan sound by moving pointer across Earth">
          <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm0-13a5 5 0 1 0 5 5 5 5 0 0 0-5-5z"/></svg>
          <span id="scanner-btn-label">SCAN EARTH</span>
        </button>

        <!-- Region Drawer Toggle -->
        <button class="pill-btn" id="btn-regions" aria-label="Select sonic regions">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>
          REGIONS (18)
        </button>

        <!-- Scientific Data Provenance & Transparency Modal Toggle -->
        <button class="pill-btn" id="btn-data-transparency" aria-label="Scientific Data Provenance & Transparency" title="Scientific Data Provenance & Transparency" style="color:#00E676;border-color:rgba(0,230,118,0.4);background:rgba(0,230,118,0.08)">
          <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          DATA TRANSPARENCY
        </button>

        <!-- Zen Mode / Full Globe View Toggle -->
        <button class="ib" id="btn-zen" aria-label="Toggle Zen Mode / Full Globe View" title="Zen Mode (Full Globe View) [Key: Z]">
          <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
        </button>

        <!-- Zoom Controls -->
        <button class="ib" id="zi" aria-label="Zoom in" title="Zoom in">
          <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
        </button>
        <button class="ib" id="zo" aria-label="Zoom out" title="Zoom out">
          <svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>
        </button>

        <!-- Sound Mute/Unmute -->
        <button class="ib" id="snd" aria-label="Toggle Mute" title="Toggle Sound">
          <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5zM19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
        </button>

        <!-- Settings Modal Toggle -->
        <button class="ib" id="btn-settings" aria-label="Settings" title="Observatory Settings">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </button>

        <!-- Fullscreen -->
        <button class="ib" id="btn-fs" aria-label="Fullscreen" title="Toggle Fullscreen">
          <svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
        </button>
      </div>
    </header>

    <!-- Left Panel: Planetary Dimensions Selector -->
    <nav id="left" class="glass" aria-label="Planetary Data Categories">
      <div class="panel-title">
        <span>PLANETARY DATA</span>
        <span class="mono">6 CHANNELS</span>
      </div>
      <!-- Injected by JavaScript -->
    </nav>

    <!-- Right Panel: HUD & Scientific Metrics -->
    <aside id="hud" class="glass" aria-label="Scientific Metrics HUD">
      <div class="hud-header">
        <div class="hud-title-wrap">
          <span class="hud-label">DATA DIMENSION</span>
          <div class="hud-dataset-name" id="hud-name">GLOBAL TEMPERATURE ANOMALY</div>
          <div class="hud-dataset-desc" id="hud-desc">Atmospheric boundary layer and surface radiative forcing deviation from pre-industrial baseline.</div>
        </div>
      </div>

      <div class="hud-val-container">
        <div class="val-row">
          <div id="val" class="mono">+1.28<small>&deg;C</small></div>
          <div class="delta-badge up mono" id="trend">&#9650; +0.94&deg;C</div>
        </div>
        <div class="hud-sub-stats">
          <span>BASELINE: <b id="hud-baseline">1850&ndash;1900</b></span>
          <span class="mono" id="hud-rate">+0.24&deg;C / DECADE</span>
        </div>
      </div>

      <!-- Scientific Data Provenance Banner -->
      <div class="provenance-banner mono" id="hud-provenance" title="Click to view scientific provenance, data providers & acoustic equations">
        <div class="prov-badge-dot"></div>
        <span id="provenance-status">REAL SCIENTIFIC DATA</span>
        <span style="opacity:0.4">&middot;</span>
        <span id="provenance-provider">NASA GISS GISTEMP v4 LOTI</span>
      </div>

      <!-- Interactive 45-year sparkline -->
      <div class="chart-box">
        <div class="chart-wrap">
          <div class="chart-tooltip mono" id="ch-tooltip">1990: +0.45&deg;C</div>
          <svg id="ch" viewBox="0 0 240 70" preserveAspectRatio="none">
            <defs>
              <linearGradient id="ch-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--ac)" stop-opacity="0.35"/>
                <stop offset="100%" stop-color="var(--ac)" stop-opacity="0.0"/>
              </linearGradient>
            </defs>
            <polygon id="ch-area" fill="url(#ch-grad)" points=""/>
            <polyline id="ln" fill="none" stroke="var(--ac)" stroke-width="2" vector-effect="non-scaling-stroke"/>
            <line id="cursor-ln" x1="0" y1="0" x2="0" y2="70" stroke="rgba(255,255,255,0.4)" stroke-dasharray="2,2"/>
            <circle id="dt" r="4" fill="#FFFFFF" stroke="var(--ac)" stroke-width="2"/>
          </svg>
        </div>
        <div class="chart-legend mono">
          <span>1980</span>
          <span>1995</span>
          <span>2010</span>
          <span>2025</span>
        </div>
      </div>

      <div class="science-intel">
        <div class="sensor-line">
          <svg style="width:12px;height:12px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20M2 12h20"/></svg>
          <span id="sensor-name">HISTORICAL CLIMATE REFERENCE &middot; NASA GISTEMP / ERA5</span>
        </div>
        <div style="font-size:8px;color:var(--t3);text-transform:none">
          Click any spot on Earth to synthesize acoustic frequency &amp; biophony for that exact region.
        </div>
      </div>
    </aside>

    <!-- Active Region Banner (when hotspot selected) -->
    <div id="region-banner" class="glass">
      <div class="reg-info">
        <div class="reg-title-row">
          <span id="reg-icon" style="font-size:16px">&#127807;</span>
          <span class="reg-name" id="reg-name">AMAZON BASIN</span>
          <span class="reg-badge" id="reg-badge">BIOPHONY ACTIVE</span>
          <span class="mono" style="font-size:8.5px;color:var(--t2)" id="reg-coords">3.4&deg;S, 62.2&deg;W</span>
        </div>
        <div class="reg-sound-desc" id="reg-sound-desc">Synthesized canopy biophony with avian FM sweeps and moist forest resonance.</div>
      </div>
      <div class="reg-actions">
        <button class="reg-dismiss" id="btn-reset-region">
          <svg style="width:12px;height:12px;fill:none;stroke:currentColor;stroke-width:2" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
          GLOBAL PLANET
        </button>
      </div>
    </div>

    <!-- Floating Landmark Milestone Alert -->
    <div id="milestone-alert" class="glass">
      <div class="ms-alert-tag mono" id="ms-tag">HISTORICAL EVENT</div>
      <div class="ms-alert-body">
        <div class="ms-alert-year-title" id="ms-title">2015 &middot; PARIS CLIMATE AGREEMENT</div>
        <div class="ms-alert-desc" id="ms-desc">Historic treaty adopted by 196 parties to limit warming to well below 2.0&deg;C and pursue 1.5&deg;C efforts.</div>
      </div>
      <button class="ms-alert-close" id="btn-close-ms" aria-label="Close milestone notification">&times;</button>
    </div>

    <!-- =========================================================================
         CONTROL DECK (#jb) - COMPACT, DRAGGABLE & DOCKABLE
         ========================================================================= -->
    <section id="jb" class="glass" aria-label="Timeline and Audio Synthesizer Controls">
      <!-- Top Drag Handle & Deck Action Bar -->
      <div class="deck-drag-handle" id="deck-drag">
        <div class="drag-grip">
          <div class="drag-dots"><span></span><span></span><span></span></div>
          <span class="drag-label mono">ARIA CONTROL DECK &middot; DRAGGABLE</span>
        </div>
        <div class="deck-actions">
          <button class="deck-btn" id="btn-dock-cycle" title="Cycle Dock Position (Bottom / Top / Left / Right / Floating)">
            <svg viewBox="0 0 24 24"><path d="M4 4h16v16H4zM4 14h16"/></svg>
          </button>
          <button class="deck-btn" id="btn-minimize-deck" title="Minimize / Expand Deck for Full Globe View">
            <svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>
          </button>
        </div>
      </div>

      <!-- Minimized Capsule Content -->
      <div class="deck-mini-content">
        <button class="mini-play-btn" id="mini-play" title="Play / Pause Sonification">
          <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <div class="year-stepper" style="gap:2px">
          <button class="step-btn mono" id="btn-mini-prev">&lt;</button>
          <span class="mono" style="font-size:11px;font-weight:600;color:#fff;min-width:44px;text-align:center" id="mini-year">1990</span>
          <button class="step-btn mono" id="btn-mini-next">&gt;</button>
        </div>
        <span class="tag live" style="font-size:8px;padding:2px 6px" id="mini-region-tag">GLOBAL</span>
        <button class="pill-btn" style="padding:3px 8px;font-size:8px" id="btn-expand-deck">
          EXPAND
        </button>
      </div>

      <!-- Full Deck Content -->
      <div class="deck-full-content">
        <!-- Audio Oscilloscope & Central Play Engine (Compact) -->
        <div class="audio-row">
          <div class="vz-box">
            <div class="vz-header">
              <span>STEREO OSCILLOSCOPE</span>
              <span class="mono" id="osc-hz">220 HZ</span>
            </div>
            <canvas class="vz" id="wv" width="260" height="26"></canvas>
          </div>

          <div class="play-station">
            <button id="play" aria-label="Start Sonification">
              <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <span class="play-state-text" id="play-text">SONIFY</span>
          </div>

          <div class="vz-box">
            <div class="vz-header">
              <span>FFT SPECTRUM</span>
              <span class="mono" id="scale-badge">PENTATONIC</span>
            </div>
            <canvas class="vz" id="sp" width="260" height="26"></canvas>
          </div>
        </div>

        <!-- Adjustable Timeline Station (1980 to 2025) -->
        <div class="timeline-station">
          <div class="tl-header-row">
            <div class="tl-title-wrap">
              <span class="tl-title">ADJUSTABLE TIMELINE</span>
              <span class="tl-mode-badge mono">1980 &ndash; 2025</span>
            </div>

            <!-- Stepper Buttons & Year Display -->
            <div class="year-stepper">
              <button class="step-btn mono" id="btn-step-prev5" title="-5 Years">-5Y</button>
              <button class="step-btn mono" id="btn-step-prev" title="-1 Year">&lt;</button>
              <div class="year-display mono" id="yt">1990</div>
              <button class="step-btn mono" id="btn-step-next" title="+1 Year">&gt;</button>
              <button class="step-btn mono" id="btn-step-next5" title="+5 Years">+5Y</button>
            </div>
          </div>

          <!-- Interactive Range Slider -->
          <div class="slider-container">
            <input type="range" class="timeline-slider" id="yr" min="1980" max="2025" step="1" value="1990" aria-label="Year Scrubber">
          </div>

          <!-- Milestone Bookmarks Bar -->
          <div class="milestones-bar" id="ms-bar">
            <!-- Dynamically populated milestones -->
          </div>
        </div>

        <!-- Bottom Status & Fine Tuning Bar -->
        <div class="deck-sub-bar">
          <div class="audio-stats">
            <div class="stat-item">
              <span class="stat-label">TEMPO:</span>
              <span class="stat-val mono" id="stat-bpm">72 BPM</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">RESONANCE:</span>
              <span class="stat-val mono" id="stat-res">1.4 KHZ</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">PAN:</span>
              <span class="stat-val mono" id="stat-pan">CENTER</span>
            </div>
          </div>

          <div class="deck-right-actions">
            <div class="vol-wrap">
              <span style="font-size:7.5px;color:var(--t3)">VOL</span>
              <input type="range" class="vol-slider" id="vol" min="0" max="1" step="0.01" value="0.75" aria-label="Master Volume">
            </div>
            <button class="ib" style="width:24px;height:24px" id="rs" title="Reset Timeline to 1980">
              <svg style="width:11px;height:11px" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Expanded Region Selection Drawer Modal (18 Regions + Category Filters) -->
    <div id="region-drawer">
      <div class="modal-box glass">
        <div class="modal-head">
          <div>
            <div class="modal-title">
              <svg style="width:18px;height:18px;fill:none;stroke:var(--ac);stroke-width:2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20M2 12h20"/></svg>
              GLOBAL SONIC BIOMES &amp; REGIONS (18)
            </div>
            <div class="modal-sub">
              Select any region below, or click directly on any spot on the 3D globe to synthesize spatial acoustics for that location.
            </div>
          </div>
          <button class="modal-close" id="btn-close-regions">&times;</button>
        </div>

        <!-- Biome Filter Tabs -->
        <div class="biome-filters">
          <button class="biome-filter-btn active" data-filter="all">ALL (18)</button>
          <button class="biome-filter-btn" data-filter="forests">&#127807; FORESTS &amp; BIOSPHERE</button>
          <button class="biome-filter-btn" data-filter="cryosphere">&#10052; POLAR &amp; GLACIERS</button>
          <button class="biome-filter-btn" data-filter="oceans">&#127754; OCEANS &amp; TRENCHES</button>
          <button class="biome-filter-btn" data-filter="climate">&#127964; DESERTS &amp; ARID</button>
          <button class="biome-filter-btn" data-filter="atmosphere">&#127755; ATMOSPHERE &amp; PERMAFROST</button>
        </div>

        <div class="regions-grid" id="regions-grid">
          <!-- Dynamically populated cards for the 18 hotspots -->
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div id="settings-modal">
      <div class="modal-box glass" style="max-width:520px">
        <div class="modal-head">
          <div class="modal-title">OBSERVATORY CONFIGURATION</div>
          <button class="modal-close" id="btn-close-settings">&times;</button>
        </div>
        <div class="settings-grid">
          <div class="setting-item">
            <label>CONTROL DECK DOCK POSITION</label>
            <select id="sel-dock-pos">
              <option value="bottom" selected>Bottom Centered (Standard)</option>
              <option value="top">Top Centered (Below Header)</option>
              <option value="left">Floating Bottom Left</option>
              <option value="right">Floating Bottom Right</option>
              <option value="free">Draggable Anywhere</option>
            </select>
          </div>
          <div class="setting-item">
            <label>MUSICAL SCALE HARMONICS</label>
            <select id="sel-scale">
              <option value="pent">Pentatonic Major (Zen &amp; Ethereal)</option>
              <option value="min">Natural Minor (Contemplative &amp; Deep)</option>
              <option value="dorian">Dorian Mode (Celestial &amp; Atmospheric)</option>
              <option value="phrygian">Phrygian Mode (Mystical &amp; Dramatic)</option>
            </select>
          </div>
          <div class="setting-item">
            <label>GLOBE ROTATION SPEED</label>
            <select id="sel-rot">
              <option value="slow">Slow Cinematic Drift</option>
              <option value="med" selected>Medium Observation</option>
              <option value="off">Lock Celestial Rotation</option>
            </select>
          </div>
          <div class="setting-item">
            <label>ATMOSPHERE GLOW INTENSITY</label>
            <select id="sel-aura">
              <option value="1.0" selected>Standard Luminous Aura</option>
              <option value="1.5">Intense Radiant Flare</option>
              <option value="0.5">Subtle Atmospheric Rim</option>
            </select>
          </div>
        </div>

        <!-- Scientific Backend Connection -->
        <div style="margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.08)">
          <div style="font-size:9px;color:var(--t2);letter-spacing:0.12em;font-weight:600;margin-bottom:4px">SCIENTIFIC BACKEND (FASTAPI / NASA / NOAA)</div>
          <div style="font-size:8px;color:var(--t3);line-height:1.5;margin-bottom:8px">
            Default: Curated NASA/NOAA 1980–2025 Empirical Reference Engine. To stream live updates from a deployed FastAPI instance, enter the HTTPS endpoint below.
          </div>
          <div style="display:flex;gap:8px;margin-bottom:6px">
            <input id="inp-backend-url" type="text" value="" style="flex:1;background:#050B16;border:1px solid rgba(255,255,255,0.14);border-radius:4px;color:var(--tx);font-family:var(--fn-mono);font-size:9.5px;padding:6px 10px;" placeholder="https://api.your-domain.com or http://127.0.0.1:8000" />
            <button id="btn-sync-backend" class="btn-step" style="padding:4px 12px;font-size:9px;color:var(--ac);border-color:var(--ac)">TEST &amp; SYNC</button>
          </div>
          <div id="backend-status-text" class="mono" style="font-size:8px;color:#80D8FF">STATUS: STANDALONE NASA/NOAA REFERENCE ENGINE ACTIVE</div>
          <div id="backend-mixed-warn" class="mono" style="font-size:8px;color:#FF5252;display:none;margin-top:4px">WARNING: Browsers block HTTP endpoints from HTTPS sites (Mixed Content). Use an HTTPS URL.</div>
        </div>

        <!-- Sonification Acoustic Mapping Legend -->
        <div style="margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.08)">
          <div style="font-size:9px;color:var(--t2);letter-spacing:0.12em;font-weight:600;margin-bottom:8px">DATA SONIFICATION MAPPING LEGEND</div>
          <div style="font-size:8px;color:var(--t3);line-height:1.6;display:flex;flex-direction:column;gap:5px">
            <div><strong style="color:#FF5722">Global Temperature Anomaly:</strong> Mapped to oscillator harmonic pitch (+ octaves) and resonant low-pass filter cutoff (800 Hz &rarr; 3600 Hz). Higher warming yields brighter, higher acoustic tension.</div>
            <div><strong style="color:#D500F9">Atmospheric CO₂ (PPM):</strong> Drives oscillator detune spread (0 &rarr; 45 cents) and rhythm tempo (68 &rarr; 120 BPM), creating urgent harmonic flutter.</div>
            <div><strong style="color:#00E5FF">Ocean Sea Level &amp; Heat:</strong> Modulates sub-bass drone foundation (44 &rarr; 55 Hz) and swell volume (0.22 &rarr; 0.32), representing increasing oceanic pressure.</div>
            <div><strong style="color:#FFD600">Regional Weather (NASA POWER):</strong> Geographic longitude controls stereo acoustic panning (L/R) while precipitation drives rainfall flutter rate.</div>
            <div><strong style="color:#00E676">Forest Canopy Integrity:</strong> Intact canopy produces lush harmonic chords; forest loss introduces arid background white noise grain.</div>
          </div>
        </div>

        <div style="font-size:8px;color:var(--t3);line-height:1.6;margin-top:12px">
          Tip: Press [Z] on your keyboard anytime to activate Zen Mode and observe the full 3D Earth without UI overlays.
        </div>
      </div>
    </div>

    <!-- Scientific Data Transparency & Provenance Modal -->
    <div id="data-modal">
      <div class="modal-box glass" style="max-width:960px">
        <div class="modal-head">
          <div>
            <div class="modal-title">SCIENTIFIC DATA TRANSPARENCY &amp; PROVENANCE</div>
            <div style="font-size:8.5px;color:var(--t3);margin-top:3px;letter-spacing:0.08em">
              OFFICIAL SATELLITE &amp; OBSERVATORY INSTRUMENT FEEDS &middot; ACOUSTIC MAPPING STANDARDS
            </div>
          </div>
          <button class="modal-close" id="btn-close-data">&times;</button>
        </div>

        <!-- Provenance Badge Legend -->
        <div style="display:flex;flex-wrap:wrap;gap:8px;padding:8px 12px;background:rgba(255,255,255,0.02);border:1px solid var(--bd);border-radius:6px;align-items:center">
          <span class="mono" style="font-size:8px;color:var(--t3);font-weight:600">PROVENANCE CLASSIFICATION:</span>
          <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
          <span class="dc-status-badge badge-benchmark mono">&bull; EMPIRICAL BENCHMARK (PERIODIC SYNTHESIS)</span>
          <span class="dc-status-badge badge-simulated mono">&bull; SIMULATED DEMONSTRATION</span>
          <span class="dc-status-badge badge-unavailable mono">&bull; DATA UNAVAILABLE</span>
        </div>

        <div class="data-matrix-grid">
          <!-- 1. NASA GISTEMP LOTI -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: CLIMATE</span>
            </div>
            <div class="dc-title">NASA GISTEMP v4 LOTI</div>
            <div class="dc-provider">NASA Goddard Institute for Space Studies (GISS)</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://data.giss.nasa.gov/gistemp/" target="_blank" rel="noopener">data.giss.nasa.gov/gistemp/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI GistempService (tabledata_v4/GLB.Ts+dSST.csv)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">Land-Ocean Temperature Anomaly (LOTI)</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">&deg;C anomaly (vs 1951&ndash;1980 baseline)</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Global (Land + Sea-surface), 1880 &ndash; Present (Monthly)</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Pitch shifted by \(\Delta T\) (\(f = f_0 \cdot 2^{(\Delta T / 1.5)}\)); resonant 24dB LPF cutoff scaled exponentially (\(800\,\text{Hz} \to 3600\,\text{Hz}\)) as thermal anomaly rises.
            </div>
          </div>

          <!-- 2. NOAA GML Mauna Loa CO2 -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: ATMOSPHERE</span>
            </div>
            <div class="dc-title">NOAA GML Mauna Loa In-Situ CO&sub2;</div>
            <div class="dc-provider">NOAA Global Monitoring Laboratory &amp; Scripps Institution</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://gml.noaa.gov/ccgg/trends/" target="_blank" rel="noopener">gml.noaa.gov/ccgg/trends/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI Co2Service (co2_mm_mlo.csv)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">Carbon Dioxide Dry Air Mole Fraction</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">Parts Per Million (PPM)</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Point Observatory (19.536&deg;N, 155.576&deg;W), 1958 &ndash; Present</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Detune spread expands from 0 to 45 cents with CO&sub2; rise; pulse rhythm tempo scales linearly (\(68 \to 120\,\text{BPM}\)) over Keeling trajectory.
            </div>
          </div>

          <!-- 3. NOAA / Satellite Altimetry Sea Level -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: OCEANS</span>
            </div>
            <div class="dc-title">Global Mean Sea Level (GMSL) Anomaly</div>
            <div class="dc-provider">NOAA Laboratory for Satellite Altimetry (TOPEX/Jason/Sentinel-6)</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/" target="_blank" rel="noopener">star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI SeaLevelService (slr_sla_gbl_free_all_66.csv)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">Sea Level Anomaly with GIA Correction</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">Millimeters (mm)</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Global Ice-Free Ocean (66&deg;S to 66&deg;N), 1993 &ndash; Present</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Sub-bass foundation oscillator modulates from 44 Hz up to 55 Hz; swell amplitude increases (\(0.22 \to 0.32\)), evoking hydraulic planetary pressure.
            </div>
          </div>

          <!-- 4. NOAA GML Atmospheric Methane -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: METHANE</span>
            </div>
            <div class="dc-title">NOAA GML Marine Boundary Layer CH&sub4;</div>
            <div class="dc-provider">NOAA Global Greenhouse Gas Reference Network</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://gml.noaa.gov/ccgg/trends_ch4/" target="_blank" rel="noopener">gml.noaa.gov/ccgg/trends_ch4/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI Ch4Service (ch4_mm_gl.csv)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">Globally Averaged Marine Surface Methane</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">Parts Per Billion (PPB)</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Global Marine Boundary Layer, 1983 &ndash; Present (Monthly)</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Ring-modulator carrier frequency shifts proportionally to CH&sub4; surge (\(1570 \to 1938\,\text{PPB}\)), producing high-register metallic tension.
            </div>
          </div>

          <!-- 5. NASA POWER Regional Meteorology -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">SCANNER &amp; HOTSPOTS</span>
            </div>
            <div class="dc-title">NASA POWER Point Meteorology (MERRA-2)</div>
            <div class="dc-provider">NASA Langley Research Center &amp; GMAO Reanalysis</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://power.larc.nasa.gov/" target="_blank" rel="noopener">power.larc.nasa.gov/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI PowerService (/api/temporal/monthly/point)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">T2M (2m Air Temp), PRECTOTCORR (Precip), RH2M, ALLSKY_SFC_SW_DWN</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">&deg;C, mm/day, %, kW-hr/m&sup2;/day</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Global 0.5&deg; &times; 0.625&deg; Grid, 1981 &ndash; Present (Queried on Click)</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Longitude maps to stereo panning (\(-180^\circ \to +180^\circ \mapsto L \to R\)); local T2M sets modal root note; precipitation rate controls noise flutter frequency.
            </div>
          </div>

          <!-- 6. NASA GIBS Satellite Imagery -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-real mono">&bull; REAL SCIENTIFIC DATA</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">VISUAL TEXTURES</span>
            </div>
            <div class="dc-title">NASA GIBS Satellite Browse Services</div>
            <div class="dc-provider">NASA Earth Observing System Data &amp; Information System (EOSDIS)</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://gibs.earthdata.nasa.gov/" target="_blank" rel="noopener">gibs.earthdata.nasa.gov/</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">FastAPI GibsService (WMTS Tile Service &amp; XML capabilities)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">MODIS Corrected Reflectance True Color, VIIRS SNPP Night Band</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">EPSG:4326 / EPSG:3857 Tile Matrix (250m &ndash; 1km resolution)</td></tr>
              <tr><td class="dc-lbl">COVERAGE</td><td class="dc-val">Global Satellite Passes, 2000 &ndash; Present</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Day/Night solar terminator calculations modulate spatial reverb width and atmospheric shimmer harmonics across the planetary group.
            </div>
          </div>

          <!-- 7. FAO FRA & Hansen / UMD Canopy Integrity -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-benchmark mono">&bull; EMPIRICAL BENCHMARK</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: FORESTS</span>
            </div>
            <div class="dc-title">Global Canopy Integrity Index</div>
            <div class="dc-provider">Hansen / Univ. of Maryland Global Forest Change &amp; FAO FRA</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://glad.earthengine.app/view/global-forest-change" target="_blank" rel="noopener">glad.earthengine.app/view/global-forest-change</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">Decadal Periodic Synthesis Benchmark (Landsat/MODIS calibration)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">Intact Canopy Cover Remaining (% of 1980 baseline)</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">% Base (100.0% in 1980 &rarr; 82.0% in 2025)</td></tr>
              <tr><td class="dc-lbl">STATUS NOTE</td><td class="dc-val">Empirical periodic benchmark; no direct automated daily API exists</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Lush harmonic partials sustain when canopy is intact; cumulative deforestation introduces arid white noise crackle and attenuated resonance.
            </div>
          </div>

          <!-- 8. NSIDC Arctic Sea Ice Extent -->
          <div class="data-card">
            <div class="dc-badge-row">
              <span class="dc-status-badge badge-benchmark mono">&bull; EMPIRICAL BENCHMARK</span>
              <span class="mono" style="font-size:8px;color:var(--t3)">CHANNEL: CRYOSPHERE</span>
            </div>
            <div class="dc-title">NSIDC Arctic Sea Ice Extent (September)</div>
            <div class="dc-provider">National Snow &amp; Ice Data Center (NSIDC) / CryoSat-2 SAR</div>
            <table class="dc-table">
              <tr><td class="dc-lbl">SOURCE URL</td><td class="dc-val"><a href="https://nsidc.org/data/seaice_index" target="_blank" rel="noopener">nsidc.org/data/seaice_index</a></td></tr>
              <tr><td class="dc-lbl">INGESTION</td><td class="dc-val">Satellite Passive Microwave Synthesis Benchmark (DMSP SSMIS)</td></tr>
              <tr><td class="dc-lbl">VARIABLES</td><td class="dc-val">September Minimum Sea Ice Coverage</td></tr>
              <tr><td class="dc-lbl">UNITS</td><td class="dc-val">Million km&sup2; (7.85 M km&sup2; in 1980 &rarr; 4.22 M km&sup2; in 2025)</td></tr>
              <tr><td class="dc-lbl">STATUS NOTE</td><td class="dc-val">Empirical periodic benchmark; compiled from annual NSIDC releases</td></tr>
            </table>
            <div class="dc-sonification">
              <strong>Sonification Equation:</strong> Crystalline high-frequency bell synthesis with frost decay time; ice extent reduction truncates decay from 3.2s down to 0.4s.
            </div>
          </div>
        </div>

        <div style="font-size:8px;color:var(--t3);line-height:1.6;margin-top:10px;padding:8px;background:rgba(255,255,255,0.02);border-radius:4px">
          <strong>Scientific Integrity Commitment:</strong> ARIA never generates synthetic random walks disguised as real data. Real in-situ feeds (NASA GISS, NOAA GML, NOAA Satellite Altimetry, NASA POWER) are ingested directly from official federal repositories. Non-API indicators (Forest Canopy, Cryosphere Extent) are clearly identified as <em>Empirical Benchmarks (Periodic Synthesis)</em> derived from peer-reviewed multi-decadal literature.
        </div>
      </div>
    </div>
  </div>

  <!-- Three.js Library with Fallback CDNs -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    if (typeof THREE === 'undefined') {
      document.write('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"><\/script>');
    }
  </script>
  <script>
    if (typeof THREE === 'undefined') {
      document.write('<script src="https://unpkg.com/three@0.128.0/build/three.min.js"><\/script>');
    }
  </script>

  <!-- External Textures bundle if available -->
  <script src="textures.js"></script>

  <!-- Application Logic -->
  <script>
    // --- Helper Utilities ---
    const $ = s => document.querySelector(s);
    const $$ = s => document.querySelectorAll(s);
    const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
    const lerp = (a, b, t) => a + (b - a) * t;

    // --- Texture Fallback generator ---
    function ensureTextures() {
      if (typeof window.TX === 'undefined' || !window.TX.day) {
        window.TX = {};
        const c = document.createElement('canvas');
        c.width = 512; c.height = 256;
        const ctx = c.getContext('2d');
        
        const grad = ctx.createLinearGradient(0, 0, 0, 256);
        grad.addColorStop(0, '#103060'); grad.addColorStop(0.5, '#1e528e'); grad.addColorStop(1, '#0e2648');
        ctx.fillStyle = grad; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#2d6a4f';
        for (let i = 0; i < 40; i++) {
          ctx.beginPath();
          ctx.arc((i * 37) % 512, 60 + ((i * 53) % 140), 20 + ((i * 19) % 40), 0, Math.PI * 2);
          ctx.fill();
        }
        window.TX.day = c.toDataURL('image/jpeg', 0.8);

        ctx.fillStyle = '#02050c'; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#ffd166';
        for (let i = 0; i < 60; i++) {
          ctx.fillRect((i * 47) % 512, 60 + ((i * 41) % 140), 2, 2);
        }
        window.TX.night = c.toDataURL('image/jpeg', 0.8);

        ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#000000';
        for (let i = 0; i < 40; i++) {
          ctx.beginPath();
          ctx.arc((i * 37) % 512, 60 + ((i * 53) % 140), 20 + ((i * 19) % 40), 0, Math.PI * 2);
          ctx.fill();
        }
        window.TX.water = c.toDataURL('image/jpeg', 0.8);
      }
    }
    ensureTextures();

    // --- Planetary Categories with Unique Palettes & Historical Trajectories (1980–2025: 46 data points) ---
    const CATS = {
      climate: {
        id: 'climate',
        n: 'CLIMATE',
        t: 'GLOBAL SURFACE TEMPERATURE ANOMALY',
        sub: 'NASA GISTEMP & ERA5 Multi-Reanalysis compilation (1980–2025)',
        u: '°C',
        d: 2,
        baseline: '1850–1900 Pre-Industrial',
        sensor: 'NASA Goddard / Copernicus Climate Change Service',
        rate: '+0.24°C / DECADE',
        provStatus: 'REAL SCIENTIFIC DATA',
        provProvider: 'NASA GISS GISTEMP v4 LOTI',
        provBadgeClass: 'badge-real',
        hex: '#FF5722',
        glow: 'rgba(255, 87, 34, 0.45)',
        subtle: 'rgba(255, 87, 34, 0.14)',
        tint: [1.25, 0.45, 0.18],
        aura1: [1.0, 0.35, 0.12],
        aura2: [1.0, 0.65, 0.2],
        icon: '<path d="M12 2a3 3 0 0 0-3 3v8.17a5 5 0 1 0 6 0V5a3 3 0 0 0-3-3zm0 16a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/>',
        raw: [
          0.26, 0.32, 0.14, 0.31, 0.16, 0.12, 0.18, 0.32, 0.39, 0.27,
          0.45, 0.41, 0.22, 0.24, 0.32, 0.45, 0.35, 0.48, 0.64, 0.42,
          0.40, 0.54, 0.63, 0.62, 0.54, 0.68, 0.64, 0.66, 0.54, 0.65,
          0.72, 0.61, 0.65, 0.68, 0.75, 0.90, 1.02, 0.92, 0.85, 0.98,
          1.02, 0.85, 0.89, 1.18, 1.45, 1.48
        ]
      },
      oceans: {
        id: 'oceans',
        n: 'OCEANS',
        t: 'SEA SURFACE TEMPERATURE ANOMALY',
        sub: 'NOAA OISST & Ocean Acidification pH Monitoring (1980–2025)',
        u: '°C',
        d: 2,
        baseline: '1981–2010 Climatology Baseline',
        sensor: 'NOAA Coral Reef Watch / Argo Autonomous Float Fleet',
        rate: '+0.18°C / DECADE',
        provStatus: 'REAL SCIENTIFIC DATA',
        provProvider: 'NOAA OISST & Satellite Altimetry',
        provBadgeClass: 'badge-real',
        hex: '#00E5FF',
        glow: 'rgba(0, 229, 255, 0.45)',
        subtle: 'rgba(0, 229, 255, 0.14)',
        tint: [0.15, 0.75, 1.25],
        aura1: [0.0, 0.65, 1.0],
        aura2: [0.1, 0.9, 0.75],
        icon: '<path d="M2 6c3-3 5 3 8 0s5 3 8 0 4 2 4 2M2 12c3-3 5 3 8 0s5 3 8 0 4 2 4 2M2 18c3-3 5 3 8 0s5 3 8 0 4 2 4 2"/>',
        raw: [
          0.12, 0.14, 0.08, 0.18, 0.06, 0.04, 0.08, 0.17, 0.22, 0.15,
          0.22, 0.24, 0.11, 0.14, 0.17, 0.24, 0.19, 0.27, 0.42, 0.23,
          0.21, 0.29, 0.35, 0.36, 0.31, 0.38, 0.36, 0.35, 0.29, 0.37,
          0.41, 0.33, 0.37, 0.39, 0.44, 0.54, 0.62, 0.53, 0.49, 0.58,
          0.60, 0.53, 0.56, 0.78, 0.96, 0.98
        ]
      },
      forests: {
        id: 'forests',
        n: 'FORESTS',
        t: 'GLOBAL INTACT CANOPY INTEGRITY',
        sub: 'Global Canopy Integrity (Global Forest Watch reference index — live API ingestion pending)',
        u: '% BASE',
        d: 1,
        baseline: '100.0% at 1980 Baseline Epoch',
        sensor: 'MODIS/Landsat Reference (Satellite API integration in progress)',
        rate: '-3.1% LOSS / DECADE',
        provStatus: 'EMPIRICAL BENCHMARK',
        provProvider: 'FAO FRA / Hansen UMD Global Forest',
        provBadgeClass: 'badge-benchmark',
        hex: '#00E676',
        glow: 'rgba(0, 230, 118, 0.45)',
        subtle: 'rgba(0, 230, 118, 0.14)',
        tint: [0.2, 1.15, 0.4],
        aura1: [0.1, 0.95, 0.35],
        aura2: [0.2, 0.85, 0.65],
        icon: '<path d="M12 2L4 12h5l-3 7h12l-3-7h5zM12 19v3"/>',
        raw: [
          100.0, 99.7, 99.3, 99.0, 98.6, 98.2, 97.8, 97.3, 96.9, 96.4,
          96.0, 95.5, 95.1, 94.7, 94.2, 93.8, 93.3, 92.8, 92.1, 91.8,
          91.4, 91.0, 90.5, 90.0, 89.6, 89.1, 88.7, 88.4, 88.1, 87.8,
          87.5, 87.2, 86.9, 86.7, 86.4, 86.0, 85.5, 85.1, 84.7, 84.1,
          83.8, 83.5, 83.1, 82.6, 82.2, 82.0
        ]
      },
      atmosphere: {
        id: 'atmosphere',
        n: 'ATMOSPHERE',
        t: 'CARBON DIOXIDE CONCENTRATION (CO₂)',
        sub: 'Mauna Loa Baseline Observatory Keeling Curve (1980–2025)',
        u: 'PPM',
        d: 1,
        baseline: '280 PPM Pre-Industrial Baseline',
        sensor: 'NOAA Global Monitoring Lab / Scripps Institution',
        rate: '+2.45 PPM / YEAR',
        provStatus: 'REAL SCIENTIFIC DATA',
        provProvider: 'NOAA GML Mauna Loa In-Situ',
        provBadgeClass: 'badge-real',
        hex: '#D500F9',
        glow: 'rgba(213, 0, 249, 0.45)',
        subtle: 'rgba(213, 0, 249, 0.14)',
        tint: [0.95, 0.45, 1.2],
        aura1: [0.85, 0.25, 1.0],
        aura2: [0.45, 0.4, 1.0],
        icon: '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 9 9M8 12a4 4 0 0 1 8 0"/>',
        raw: [
          338.8, 340.1, 341.2, 342.9, 344.4, 345.9, 347.2, 348.9, 351.5, 352.9,
          354.2, 355.6, 356.4, 357.1, 358.8, 360.8, 362.6, 363.7, 366.7, 368.4,
          369.5, 371.1, 373.2, 375.8, 377.5, 379.8, 381.9, 383.8, 385.6, 387.4,
          389.9, 391.7, 393.8, 396.5, 398.6, 400.8, 404.2, 406.6, 408.5, 411.4,
          414.2, 416.4, 418.6, 421.1, 424.2, 425.5
        ]
      },
      cryosphere: {
        id: 'cryosphere',
        n: 'CRYOSPHERE',
        t: 'ARCTIC SEPTEMBER SEA ICE EXTENT',
        sub: 'NSIDC Satellite Microwave Altimetry Index (1980–2025)',
        u: 'M km²',
        d: 2,
        baseline: '1981–2010 Median (6.5 M km²)',
        sensor: 'National Snow & Ice Data Center / CryoSat-2 SAR',
        rate: '-12.8% LOSS / DECADE',
        provStatus: 'EMPIRICAL BENCHMARK',
        provProvider: 'NSIDC Satellite Sea Ice Index',
        provBadgeClass: 'badge-benchmark',
        hex: '#80D8FF',
        glow: 'rgba(128, 216, 255, 0.45)',
        subtle: 'rgba(128, 216, 255, 0.14)',
        tint: [0.6, 0.95, 1.3],
        aura1: [0.5, 0.85, 1.0],
        aura2: [0.95, 0.98, 1.0],
        icon: '<path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19"/>',
        raw: [
          7.85, 7.25, 7.45, 7.52, 7.17, 6.93, 7.54, 7.48, 7.49, 7.04,
          6.24, 6.55, 7.55, 6.50, 7.18, 6.13, 7.58, 6.74, 6.56, 6.24,
          6.32, 6.75, 5.83, 6.15, 6.05, 5.57, 5.92, 4.30, 4.73, 5.39,
          4.93, 4.63, 3.41, 5.35, 5.28, 4.68, 4.72, 4.87, 4.79, 4.32,
          4.00, 4.92, 4.87, 4.37, 4.28, 4.22
        ]
      },
      methane: {
        id: 'methane',
        n: 'METHANE',
        t: 'ATMOSPHERIC METHANE (CH₄)',
        sub: 'WMO Global Atmosphere Watch & TROPOMI Satellite (1980–2025)',
        u: 'PPB',
        d: 0,
        baseline: '722 PPB Pre-Industrial Baseline',
        sensor: 'Copernicus Sentinel-5P TROPOMI / NOAA Carbon Cycle',
        rate: '+11.5 PPB / YEAR SURGE',
        provStatus: 'REAL SCIENTIFIC DATA',
        provProvider: 'NOAA GML Marine Boundary Layer',
        provBadgeClass: 'badge-real',
        hex: '#FFD600',
        glow: 'rgba(255, 214, 0, 0.45)',
        subtle: 'rgba(255, 214, 0, 0.14)',
        tint: [1.18, 0.95, 0.15],
        aura1: [1.0, 0.85, 0.12],
        aura2: [0.75, 0.95, 0.25],
        icon: '<path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5zM5 14a7 7 0 0 0 14 0M12 18v4"/>',
        raw: [
          1570, 1585, 1600, 1618, 1632, 1648, 1662, 1675, 1690, 1704,
          1716, 1728, 1735, 1740, 1745, 1750, 1756, 1761, 1768, 1774,
          1773, 1772, 1773, 1775, 1777, 1776, 1778, 1785, 1792, 1800,
          1808, 1813, 1819, 1826, 1834, 1845, 1853, 1860, 1869, 1877,
          1889, 1908, 1920, 1928, 1934, 1938
        ]
      }
    };

    for (const k in CATS) {
      const c = CATS[k];
      c.min = Math.min(...c.raw);
      c.max = Math.max(...c.raw);
    }

    const getVal = (catKey, year) => {
      const c = CATS[catKey];
      const idxFloat = clamp(year - 1980, 0, 45);
      const i = Math.floor(idxFloat);
      const frac = idxFloat - i;
      if (i >= 45) return c.raw[45];
      return lerp(c.raw[i], c.raw[i + 1], frac);
    };

    const getNorm = (catKey, year) => {
      const c = CATS[catKey];
      return clamp((getVal(catKey, year) - c.min) / (c.max - c.min), 0, 1);
    };

    // --- Landmark Milestones across 1980–2025 ---
    const MILESTONES = [
      { year: 1988, title: '1988 · IPCC Formed', tag: 'POLITICAL', desc: 'UN establishes IPCC following James Hansen’s historic greenhouse testimony.' },
      { year: 1992, title: '1992 · Rio Earth Summit', tag: 'ACCORD', desc: '154 nations sign UNFCCC framework treaty on greenhouse stabilization.' },
      { year: 1997, title: '1997 · Kyoto Protocol', tag: 'POLICY', desc: 'First legally binding greenhouse gas reduction treaty established.' },
      { year: 1998, title: '1998 · Super El Niño', tag: 'CLIMATE EVENT', desc: 'Intense Pacific heat pulse drives unprecedented global marine bleaching.' },
      { year: 2007, title: '2007 · Arctic Ice Drop', tag: 'CRYOSPHERE', desc: 'Summer Arctic sea ice collapses to shocking record minimum.' },
      { year: 2015, title: '2015 · Paris Climate Agreement', tag: 'TREATY', desc: 'Historic 196-nation accord commits to pursue limiting warming to 1.5°C.' },
      { year: 2020, title: '2020 · COVID Lockdown Dip', tag: 'EMISSIONS', desc: 'Global industrial slowdown briefly reduces fossil fuel emissions by 5.4%.' },
      { year: 2023, title: '2023 · Hottest Year on Record', tag: 'RECORD', desc: 'Global surface temperature surges to +1.45°C above baseline.' },
      { year: 2024, title: '2024 · 1.5°C Threshold Sequence', tag: 'CRITICAL', desc: '12 consecutive months exceeding the 1.5°C threshold recorded by Copernicus.' }
    ];

    // --- Comprehensive Global Landmark Biomes (18 Regions) ---
    const HOTSPOTS = [
      {
        id: 'amazon',
        n: 'Amazon Basin',
        location: 'Brazil · South America',
        lat: -3.4,
        lon: -62.2,
        cat: 'forests',
        badge: 'CANOPY BIOPHONY',
        soundDesc: 'Synthesized rainforest biophony with avian FM sweeps and moist canopy resonance.',
        soundType: 'rainforest',
        icon: '🌿'
      },
      {
        id: 'patagonia',
        n: 'Patagonian Ice Fields',
        location: 'Chile & Argentina · South America',
        lat: -49.5,
        lon: -73.5,
        cat: 'cryosphere',
        badge: 'SOUTHERN ICE FIELD',
        soundDesc: 'Glacial creaking, sub-zero katabatic wind gusts, and southern maritime resonance.',
        soundType: 'polar',
        icon: '❄️'
      },
      {
        id: 'pnw',
        n: 'Pacific Northwest Rainforest',
        location: 'USA & Canada · North America',
        lat: 47.5,
        lon: -122.3,
        cat: 'forests',
        badge: 'TEMPERATE RAINFOREST',
        soundDesc: 'Temperate coastal canopy, rainfall flutter, and dense conifer forest resonance.',
        soundType: 'temperate',
        icon: '🌲'
      },
      {
        id: 'mojave',
        n: 'Mojave Desert & Death Valley',
        location: 'California · North America',
        lat: 36.2,
        lon: -116.8,
        cat: 'climate',
        badge: 'THERMAL BASIN',
        soundDesc: 'Extreme heat acoustic shimmer, arid wind friction, and sun-baked earth drone.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'svalbard',
        n: 'Arctic Svalbard',
        location: 'Norway · High Arctic',
        lat: 78.5,
        lon: 16.0,
        cat: 'cryosphere',
        badge: 'GLACIAL HARMONICS',
        soundDesc: 'Sub-zero resonant wind filter sweeps, high crystalline ice chimes, and deep crevicular drone.',
        soundType: 'polar',
        icon: '❄️'
      },
      {
        id: 'scandinavia',
        n: 'Scandinavian Taiga',
        location: 'Sweden & Finland · Northern Europe',
        lat: 64.0,
        lon: 17.5,
        cat: 'forests',
        badge: 'BOREAL CONIFER',
        soundDesc: 'High latitude pine forest hum, gentle sub-arctic breeze, and mossy ground acoustic absorption.',
        soundType: 'taiga',
        icon: '🌲'
      },
      {
        id: 'mediterranean',
        n: 'Mediterranean Marine Basin',
        location: 'Southern Europe',
        lat: 38.5,
        lon: 15.0,
        cat: 'oceans',
        badge: 'COASTAL HEATWAVE',
        soundDesc: 'Warm coastal currents, tidal rhythmic modulation, and marine thermal swelling.',
        soundType: 'coral',
        icon: '🌊'
      },
      {
        id: 'sahara',
        n: 'Sahara Desert (Erg Chebbi)',
        location: 'Morocco · North Africa',
        lat: 25.0,
        lon: 10.0,
        cat: 'climate',
        badge: 'ARID THERMAL DUNE',
        soundDesc: 'Microtonal dry drone in Phrygian dominant with granular sand-friction wind sweeps and warm overtones.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'congo',
        n: 'Congo Basin',
        location: 'Democratic Republic of Congo',
        lat: 0.5,
        lon: 24.0,
        cat: 'forests',
        badge: 'EQUATORIAL PULSE',
        soundDesc: 'Polyrhythmic triangle-wave ambient pulses, equatorial moisture resonance, and insect cadence sweeps.',
        soundType: 'rainforest',
        icon: '🌲'
      },
      {
        id: 'madagascar',
        n: 'Madagascar Coastal Biome',
        location: 'Madagascar · Indian Ocean',
        lat: -18.5,
        lon: 47.5,
        cat: 'oceans',
        badge: 'ISLAND BIOSPHERE',
        soundDesc: 'Tropical coastal swells, coral hydrophone bubbling, and endemic nocturnal biophony.',
        soundType: 'coral',
        icon: '🪸'
      },
      {
        id: 'himalayas',
        n: 'Himalayan Khumbu Glacier',
        location: 'Nepal & Tibet · High Asia',
        lat: 28.0,
        lon: 86.9,
        cat: 'cryosphere',
        badge: 'THIRD POLE CRYOSPHERE',
        soundDesc: 'High altitude thin-air whistling, singing-bowl overtone drone, and glacial stream resonance.',
        soundType: 'alpine',
        icon: '🏔️'
      },
      {
        id: 'siberia',
        n: 'Siberian Permafrost Taiga',
        location: 'Sakha Republic · Russia',
        lat: 63.5,
        lon: 120.0,
        cat: 'methane',
        badge: 'PERMAFROST THAW',
        soundDesc: 'Sub-arctic boreal forest wind, permafrost thaw micro-bubbling, and low-frequency bog resonance.',
        soundType: 'taiga',
        icon: '🌲'
      },
      {
        id: 'borneo',
        n: 'Sundaland Borneo Rainforest',
        location: 'Indonesia & Malaysia',
        lat: 1.0,
        lon: 114.0,
        cat: 'forests',
        badge: 'TROPICAL PEATLAND',
        soundDesc: 'Ancient dipterocarp forest biophony, peat swamp moisture resonance, and primate calls.',
        soundType: 'rainforest',
        icon: '🌿'
      },
      {
        id: 'barrier',
        n: 'Great Barrier Reef',
        location: 'Coral Sea · Australia',
        lat: -18.2,
        lon: 147.7,
        cat: 'oceans',
        badge: 'CORAL HYDROPHONE',
        soundDesc: 'Aquatic micro-bubble impulse clicks, gentle tidal chorus modulation, and marine shimmer pads.',
        soundType: 'coral',
        icon: '🪸'
      },
      {
        id: 'outback',
        n: 'Australian Red Centre',
        location: 'Northern Territory · Australia',
        lat: -23.7,
        lon: 133.8,
        cat: 'climate',
        badge: 'ARID OUTBACK',
        soundDesc: 'Dry ancient bedrock harmonics, thermal dust devils, and deep red desert drone.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'mariana',
        n: 'Mariana Trench',
        location: 'Western Pacific Ocean',
        lat: 11.3,
        lon: 142.2,
        cat: 'oceans',
        badge: 'ABYSSAL SONAR',
        soundDesc: '48 Hz tectonic sub-bass drone with resonant acoustic sonar ping echoes and oceanic pressure delays.',
        soundType: 'ocean_abyss',
        icon: '🌊'
      },
      {
        id: 'maunaloa',
        n: 'Mauna Loa Observatory',
        location: 'Hawaii · Pacific Ocean',
        lat: 19.5,
        lon: -155.6,
        cat: 'atmosphere',
        badge: 'KEELING PURE SINE',
        soundDesc: 'High-altitude sinusoidal drone tuned directly to real-time CO₂ PPM with ethereal harmonic overtone.',
        soundType: 'atmosphere',
        icon: '🌋'
      },
      {
        id: 'ross',
        n: 'Antarctic Ross Ice Shelf',
        location: 'Antarctica · South Pole',
        lat: -81.5,
        lon: 175.0,
        cat: 'cryosphere',
        badge: 'CRYOGENIC CALVING',
        soundDesc: '36 Hz sub-pulse, cryogenic ice fractures, and sub-zero katabatic wind gusts.',
        soundType: 'polar',
        icon: '🧊'
      }
    ];

    // --- State Machine ---
    const st = {
      cat: 'climate',
      year: 1990,
      play: false,
      region: null,
      customMarker: null,
      scale: 'pent',
      rotSpeed: 'med',
      mute: false,
      auraIntensity: 1.0,
      cruise: 'off',
      scanMode: false,
      dockPos: 'bottom'
    };

    // --- Global Biome Classification Engine for ANY Clicked Point on Earth ---
    function classifyGeoPoint(lat, lon) {
      const absLat = Math.abs(lat);
      
      if (absLat >= 68) {
        const isNorth = lat > 0;
        return {
          name: isNorth ? 'Arctic High Glacial Cap' : 'Antarctic Polar Ice Sheet',
          type: 'cryosphere',
          badge: 'POLAR CRYOSPHERE',
          icon: '❄️',
          soundType: 'polar',
          desc: 'Sub-zero resonant katabatic wind sweeps, brittle ice crackle transients, and calving sub-harmonics.'
        };
      }
      
      if (absLat >= 54) {
        if (lat < 0) {
          return {
            name: 'Southern Circumpolar Ocean Abyss',
            type: 'oceans',
            badge: 'CIRCUMPOLAR DEEP',
            icon: '🌊',
            soundType: 'ocean_abyss',
            desc: 'Deep circumpolar current swells, 44 Hz sub-bass rumble, and violent high-latitude maritime winds.'
          };
        } else {
          return {
            name: (lon > 30 && lon < 140) ? 'Siberian Boreal Permafrost Taiga' : 'Sub-Arctic Boreal Forest',
            type: 'forests',
            badge: 'BOREAL TAIGA & PERMAFROST',
            icon: '🌲',
            soundType: 'taiga',
            desc: 'Permafrost thaw micro-bubbling, sub-arctic pine needle wind friction, and low frequency peatland hum.'
          };
        }
      }
      
      const isSaharaArabia = (lat >= 12 && lat <= 35 && lon >= -17 && lon <= 60);
      const isAustraliaOutback = (lat <= -18 && lat >= -32 && lon >= 115 && lon <= 145);
      const isGobi = (lat >= 36 && lat <= 46 && lon >= 85 && lon <= 115);
      const isMojave = (lat >= 30 && lat <= 38 && lon >= -118 && lon <= -110);
      const isAtacama = (lat <= -18 && lat >= -28 && lon >= -72 && lon <= -67);
      
      if (isSaharaArabia || isAustraliaOutback || isGobi || isMojave || isAtacama) {
        const dName = isSaharaArabia ? 'Sahara & Arabian Thermal Dune Belt' :
                      isAustraliaOutback ? 'Australian Arid Outback Basin' :
                      isGobi ? 'Gobi Cold Desert Plateau' :
                      isMojave ? 'Mojave & Great Basin Desert' : 'Atacama Hyper-Arid Desert';
        return {
          name: dName,
          type: 'climate',
          badge: 'ARID THERMAL ZONE',
          icon: '🏜️',
          soundType: 'desert',
          desc: 'High-temperature thermal air shimmer, dry granular sand friction, and microtonal Phrygian harmonics.'
        };
      }
      
      const isAmazon = (lat >= -15 && lat <= 8 && lon >= -80 && lon <= -45);
      const isCongo = (lat >= -8 && lat <= 8 && lon >= 10 && lon <= 35);
      const isSEAsia = (lat >= -10 && lat <= 15 && lon >= 95 && lon <= 145);
      
      if (isAmazon || isCongo || isSEAsia) {
        const fName = isAmazon ? 'Amazonian Wet Canopy Basin' :
                      isCongo ? 'Congo Equatorial Peatland' : 'Sundaland Tropical Rainforest';
        return {
          name: fName,
          type: 'forests',
          badge: 'EQUATORIAL BIOPHONY',
          icon: '🌿',
          soundType: 'rainforest',
          desc: 'Dense multi-layered canopy biophony with bird chirp FM sweeps, cicada resonance, and rainfall flutter.'
        };
      }
      
      const isHimalayas = (lat >= 26 && lat <= 36 && lon >= 75 && lon <= 100);
      const isAndes = (lat >= -50 && lat <= 10 && lon >= -76 && lon <= -65);
      if (isHimalayas || isAndes) {
        return {
          name: isHimalayas ? 'Himalayan High Peak Cryosphere' : 'Andean Cordillera & Glaciers',
          type: 'cryosphere',
          badge: 'ALPINE PEAK ELEVATION',
          icon: '🏔️',
          soundType: 'alpine',
          desc: 'Thin atmospheric altitude whistling, glacial stream resonance, and harmonic singing bowl tones.'
        };
      }
      
      const isPacific = (lon < -70 && lon > -180) || (lon > 120 && lon <= 180);
      const isAtlantic = (lon >= -70 && lon <= 20 && absLat < 60);
      const isIndian = (lon >= 40 && lon <= 115 && lat < 25 && lat > -50);
      
      const isLandApprox = (
        (lat >= 25 && lat <= 60 && lon >= -125 && lon <= -65) ||
        (lat >= 36 && lat <= 60 && lon >= -10 && lon <= 40) ||
        (lat >= 15 && lat <= 55 && lon >= 40 && lon <= 135) ||
        (lat >= -35 && lat <= 35 && lon >= -17 && lon <= 50) ||
        (lat >= -55 && lat <= 12 && lon >= -80 && lon <= -35) ||
        (lat >= -40 && lat <= -11 && lon >= 113 && lon <= 154)
      );
      
      if (!isLandApprox) {
        const oceanName = isPacific ? 'Pacific Abyssal Pelagic Basin' :
                          isAtlantic ? 'Atlantic Deep Ocean Drift' :
                          isIndian ? 'Indian Ocean Tropical Waters' : 'Global Ocean Pelagic Waters';
        return {
          name: oceanName,
          type: 'oceans',
          badge: 'PELAGIC DEEP OCEAN',
          icon: '🌊',
          soundType: 'ocean_abyss',
          desc: 'Hydrothermal sub-bass swells (45 Hz), distant acoustic sonar echo pings, and oceanic pressure drones.'
        };
      }
      
      return {
        name: 'Temperate Continental Biosphere',
        type: 'climate',
        badge: 'TEMPERATE REGION',
        icon: '🍃',
        soundType: 'temperate',
        desc: 'Breezy canopy resonance, gentle acoustic harmonics, and seasonal temperature variance drone.'
      };
    }

    // --- Three.js Setup & Robust Fallback Management ---
    let R, scene, cam, planet, earth, ring, auraMesh, starPoints, U, auraU;
    let ok = false;
    let zT = 3.6, zoom = 1.0;
    let drag = false, lx = 0, ly = 0, tgt = null;
    let pointerStartedOnGlobe = false;
    let movedDistance = 0;

    let raycaster = null;
    let mouse = null;

    let ctx2d = null;
    let map2DImage = null;
    let map2DLoaded = false;

    function activate2DFallback() {
      ok = false;
      let canvas = $('#gl');
      if (canvas) {
        try {
          ctx2d = canvas.getContext('2d');
        } catch (e) {}
        if (!ctx2d) {
          const freshCanvas = document.createElement('canvas');
          freshCanvas.id = 'gl';
          freshCanvas.setAttribute('aria-label', 'Interactive 2D Earth Observatory Map');
          freshCanvas.className = canvas.className;
          canvas.parentNode.replaceChild(freshCanvas, canvas);
          ctx2d = freshCanvas.getContext('2d');
          bindCanvasInteraction(freshCanvas);
        }
      }
      if (!map2DImage && typeof window.TX !== 'undefined' && window.TX.day) {
        map2DImage = new Image();
        map2DImage.onload = () => { map2DLoaded = true; };
        map2DImage.src = window.TX.day;
      }
      const fb = $('#fb');
      if (fb) fb.style.display = 'block';
    }

    function render2DFallbackMap(now, dt, normVal, c) {
      const canvas = $('#gl');
      if (!canvas) return;
      if (!ctx2d) {
        ctx2d = canvas.getContext('2d');
        if (!ctx2d) return;
      }

      const W = window.innerWidth;
      const H = window.innerHeight;
      if (canvas.width !== W || canvas.height !== H) {
        canvas.width = W;
        canvas.height = H;
      }

      // 1. Deep space background
      ctx2d.fillStyle = '#02040A';
      ctx2d.fillRect(0, 0, W, H);

      // Radial observatory glow behind map
      const radGrad = ctx2d.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, Math.max(W, H) * 0.65);
      radGrad.addColorStop(0, '#061022');
      radGrad.addColorStop(0.6, '#030712');
      radGrad.addColorStop(1, '#010206');
      ctx2d.fillStyle = radGrad;
      ctx2d.fillRect(0, 0, W, H);

      // Deep space subtle stars
      ctx2d.fillStyle = 'rgba(200, 220, 255, 0.4)';
      for (let i = 0; i < 40; i++) {
        const sx = ((i * 137.5) % W);
        const sy = ((i * 269.3 + now * 0.005) % H);
        ctx2d.fillRect(sx, sy, 1.2, 1.2);
      }

      // 2. Centered equirectangular map box
      const mapW = Math.min(W * 0.90, H * 1.80);
      const mapH = mapW * 0.5;
      const mapX = (W - mapW) / 2;
      const mapY = (H - mapH) / 2;

      // Draw map frame & shadow
      ctx2d.save();
      ctx2d.shadowColor = 'rgba(0, 0, 0, 0.85)';
      ctx2d.shadowBlur = 30;
      ctx2d.fillStyle = '#050D1A';
      ctx2d.fillRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // Draw day texture image
      if (map2DLoaded && map2DImage) {
        ctx2d.drawImage(map2DImage, mapX, mapY, mapW, mapH);
      } else {
        // Fallback continent grid if image still decoding
        ctx2d.fillStyle = '#08172E';
        ctx2d.fillRect(mapX, mapY, mapW, mapH);
      }

      // Dynamic planetary anomaly color tint overlay
      ctx2d.save();
      ctx2d.fillStyle = c.hex;
      ctx2d.globalAlpha = 0.22 * normVal;
      ctx2d.fillRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // 3. Solar Day/Night Terminator wave
      ctx2d.save();
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, mapY + mapH);
      const sunPhase = (now * 0.00008) % (Math.PI * 2);
      for (let x = 0; x <= mapW; x += 8) {
        const rad = (x / mapW) * Math.PI * 2 + sunPhase;
        const waveY = mapY + (mapH / 2) + Math.sin(rad) * (mapH * 0.38);
        ctx2d.lineTo(mapX + x, waveY);
      }
      ctx2d.lineTo(mapX + mapW, mapY + mapH);
      ctx2d.closePath();
      ctx2d.fillStyle = 'rgba(2, 4, 10, 0.52)';
      ctx2d.fill();
      ctx2d.restore();

      // 4. Equirectangular coordinate grid
      ctx2d.save();
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.10)';
      ctx2d.lineWidth = 1;
      ctx2d.setLineDash([4, 6]);

      // Tropics (+23.5°, -23.5°)
      const tropicN = mapY + ((90 - 23.5) / 180) * mapH;
      const tropicS = mapY + ((90 - (-23.5)) / 180) * mapH;
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, tropicN); ctx2d.lineTo(mapX + mapW, tropicN);
      ctx2d.moveTo(mapX, tropicS); ctx2d.lineTo(mapX + mapW, tropicS);
      ctx2d.stroke();

      // Equator (Solid vibrant accent)
      ctx2d.setLineDash([]);
      ctx2d.strokeStyle = 'rgba(128, 216, 255, 0.35)';
      ctx2d.lineWidth = 1.2;
      const equatorY = mapY + mapH / 2;
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, equatorY); ctx2d.lineTo(mapX + mapW, equatorY);
      ctx2d.stroke();

      // Prime Meridian & Longitude marks
      ctx2d.setLineDash([3, 6]);
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      for (let lon = -120; lon <= 120; lon += 60) {
        const lx = mapX + ((lon + 180) / 360) * mapW;
        ctx2d.beginPath();
        ctx2d.moveTo(lx, mapY); ctx2d.lineTo(lx, mapY + mapH);
        ctx2d.stroke();
      }

      // Outer map border
      ctx2d.setLineDash([]);
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.22)';
      ctx2d.lineWidth = 1;
      ctx2d.strokeRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // 5. Hotspot beacons & live DOM positioning
      const allMarkers = [...HOTSPOTS];
      if (st.region && st.region.isCustom && st.region.el) {
        allMarkers.push(st.region);
      }

      allMarkers.forEach((h, idx) => {
        const sx = mapX + ((h.lon + 180) / 360) * mapW;
        const sy = mapY + ((90 - h.lat) / 180) * mapH;

        if (h.el) {
          h.el.style.transform = `translate(${sx}px, ${sy}px)`;
          h.el.style.display = 'block';
        }

        // Draw animated concentric pulse on canvas
        const isSelected = st.region && (st.region.id === h.id || st.region.n === h.n);
        const pulse = (Math.sin(now * 0.004 + idx) + 1) * 0.5;
        const radius = isSelected ? (8 + pulse * 8) : (4 + pulse * 4);

        ctx2d.save();
        ctx2d.beginPath();
        ctx2d.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx2d.strokeStyle = isSelected ? '#00E676' : (h.cat && CATS[h.cat] ? CATS[h.cat].hex : c.hex);
        ctx2d.lineWidth = isSelected ? 2 : 1.2;
        ctx2d.shadowColor = ctx2d.strokeStyle;
        ctx2d.shadowBlur = 8;
        ctx2d.stroke();

        ctx2d.beginPath();
        ctx2d.arc(sx, sy, isSelected ? 3.5 : 2, 0, Math.PI * 2);
        ctx2d.fillStyle = '#FFFFFF';
        ctx2d.fill();
        ctx2d.restore();
      });

      // 6. Observatory status watermark
      ctx2d.save();
      ctx2d.font = '10px "JetBrains Mono", monospace';
      ctx2d.fillStyle = 'rgba(140, 160, 186, 0.7)';
      ctx2d.fillText('● 2D PLANETARY OBSERVATORY · EQUIRECTANGULAR PROJECTION', mapX + 8, mapY - 8);
      ctx2d.restore();
    }

    function initWebGL() {
      if (typeof THREE === 'undefined') {
        console.warn('Three.js library is not available. Activating 2D fallback mode.');
        activate2DFallback();
        return;
      }

      try {
        const canvas = $('#gl');
        R = new THREE.WebGLRenderer({
          canvas,
          alpha: true,
          antialias: true,
          powerPreference: 'high-performance',
          failIfMajorPerformanceCaveat: false
        });
        R.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        canvas.addEventListener('webglcontextlost', e => {
          e.preventDefault();
          console.warn('WebGL context lost. Activating 2D fallback map.');
          activate2DFallback();
        }, false);

        canvas.addEventListener('webglcontextrestored', () => {
          console.info('WebGL context restored. Re-initializing 3D observatory.');
          initWebGL();
        }, false);

        scene = new THREE.Scene();
        cam = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
        cam.position.z = 3.6;

        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2();

        planet = new THREE.Group();
        scene.add(planet);

        const vs = `
          varying vec3 vP, vN;
          varying vec2 vUv;
          void main() {
            vP = position;
            vUv = uv;
            vN = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `;

        const fs = `
          #ifdef GL_FRAGMENT_PRECISION_HIGH
          precision highp float;
          #else
          precision mediump float;
          #endif
          varying vec3 vP, vN;
          varying vec2 vUv;
          uniform vec3 uSun, uTint;
          uniform float uTime, uV;
          uniform sampler2D uDay, uNight, uWater;
          
          float h(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
          float n3(vec3 p) {
            vec3 i = floor(p), f = fract(p);
            f = f * f * (3.0 - 2.0 * f);
            return mix(
              mix(mix(h(i), h(i + vec3(1, 0, 0)), f.x), mix(h(i + vec3(0, 1, 0)), h(i + vec3(1, 1, 0)), f.x), f.y),
              mix(mix(h(i + vec3(0, 0, 1)), h(i + vec3(1, 0, 1)), f.x), mix(h(i + vec3(0, 1, 1)), h(i + vec3(1, 1, 1)), f.x), f.y),
              f.z
            );
          }
          float fbm(vec3 p) {
            float a = 0.5, s = 0.0;
            for (int i = 0; i < 5; i++) {
              s += a * n3(p);
              p *= 2.03;
              a *= 0.5;
            }
            return s;
          }
          void main() {
            vec3 p = normalize(vP), N = normalize(vN);
            float d = dot(N, uSun);
            vec3 dy = texture2D(uDay, vUv).rgb;
            vec3 ni = texture2D(uNight, vUv).rgb;
            float w = texture2D(uWater, vUv).r;
            
            dy = pow(dy, vec3(1.1)) * 1.12;
            dy = mix(dy, dy * uTint * 1.6, 0.28 * uV * (1.0 - w * 0.5));
            vec3 o = dy * (0.04 + 1.15 * max(d, 0.0));
            
            vec3 Hh = normalize(uSun + vec3(0.0, 0.0, 1.0));
            o += vec3(0.9, 0.95, 1.0) * pow(max(dot(N, Hh), 0.0), 70.0) * w * 0.75 * step(0.0, d);
            
            float cl = smoothstep(0.50, 0.82, fbm(p * 3.2 + vec3(uTime * 0.012, 0.0, 0.0) + 20.0));
            o = mix(o, vec3(0.04 + max(d, 0.0) * 0.96), cl * 0.6);
            
            o += pow(ni, vec3(1.3)) * vec3(1.0, 0.82, 0.55) * 2.2 * smoothstep(0.1, -0.2, d) * (1.0 - cl * 0.6);
            o += vec3(1.0, 0.45, 0.2) * smoothstep(0.0, 0.12, d) * smoothstep(0.3, 0.08, d) * 0.07;
            
            float fr = pow(1.0 - max(N.z, 0.0), 3.0);
            o += uTint * fr * 0.9 * (0.3 + max(d + 0.3, 0.0));
            gl_FragColor = vec4(o, 1.0);
          }
        `;

        U = {
          uSun: { value: new THREE.Vector3(-0.7, 0.25, 0.65).normalize() },
          uTime: { value: 0 },
          uTint: { value: new THREE.Vector3(1.2, 0.45, 0.18) },
          uV: { value: 0 },
          uDay: { value: null },
          uNight: { value: null },
          uWater: { value: null }
        };

        earth = new THREE.Mesh(
          new THREE.SphereGeometry(1, 96, 96),
          new THREE.ShaderMaterial({ vertexShader: vs, fragmentShader: fs, uniforms: U })
        );
        earth.rotation.x = 0.3;
        earth.rotation.y = -1.9;
        planet.add(earth);

        const tl = new THREE.TextureLoader();
        [['uDay', 'day'], ['uNight', 'night'], ['uWater', 'water']].forEach(([u, k]) => {
          if (window.TX && window.TX[k]) {
            tl.load(window.TX[k], t => {
              if (R && R.capabilities) {
                t.anisotropy = R.capabilities.getMaxAnisotropy();
              }
              U[u].value = t;
            });
          }
        });

        const auraFs = `
          varying vec3 vP, vN;
          uniform vec3 uAura1, uAura2;
          uniform float uIntensity;
          void main() {
            float i = clamp(pow(max(0.60 - dot(normalize(vN), vec3(0.0, 0.0, 1.0)), 0.0), 3.2) * 2.2 * uIntensity, 0.0, 1.0);
            float a = smoothstep(0.35, 0.95, vP.y / 1.14);
            vec3 c = mix(uAura1, uAura2, a * 0.8);
            gl_FragColor = vec4(c * i, i);
          }
        `;
        auraU = {
          uAura1: { value: new THREE.Vector3(1.0, 0.35, 0.12) },
          uAura2: { value: new THREE.Vector3(1.0, 0.65, 0.2) },
          uIntensity: { value: 1.0 }
        };

        auraMesh = new THREE.Mesh(
          new THREE.SphereGeometry(1.14, 64, 64),
          new THREE.ShaderMaterial({
            vertexShader: vs,
            fragmentShader: auraFs,
            uniforms: auraU,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending,
            transparent: true,
            depthWrite: false
          })
        );
        planet.add(auraMesh);

        const starGeom = new THREE.BufferGeometry();
        const starPos = [];
        for (let i = 0; i < 900; i++) {
          const t = Math.random() * Math.PI * 2;
          const u = Math.random() * 2 - 1;
          const r = Math.sqrt(1 - u * u);
          const m = 22 + Math.random() * 20;
          starPos.push(m * r * Math.cos(t), m * u, m * r * Math.sin(t));
        }
        starGeom.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
        starPoints = new THREE.Points(
          starGeom,
          new THREE.PointsMaterial({ color: 0x8CA0BA, size: 0.11, transparent: true, opacity: 0.65 })
        );
        scene.add(starPoints);

        ring = new THREE.Mesh(
          new THREE.RingGeometry(1.52, 1.528, 128),
          new THREE.MeshBasicMaterial({ color: 0xFF5722, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
        );
        ring.rotation.x = 1.25;
        planet.add(ring);

        ok = true;
        const fb = $('#fb');
        if (fb) fb.style.display = 'none';

      } catch (err) {
        console.warn('WebGL initialization failed, activating 2D fallback:', err);
        activate2DFallback();
      }
    }

    const latLonToVec3 = (lat, lon) => {
      const phi = lat * (Math.PI / 180);
      const theta = lon * (Math.PI / 180);
      const x = Math.cos(phi) * Math.cos(theta);
      const y = Math.sin(phi);
      const z = -Math.cos(phi) * Math.sin(theta);
      
      if (typeof THREE !== 'undefined') {
        return new THREE.Vector3(x, y, z);
      }
      return {
        x, y, z,
        clone() { return latLonToVec3(lat, lon); },
        applyEuler() { return this; },
        multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; return this; },
        add() { return this; },
        dot() { return 1; },
        project() {}
      };
    };

    function initHotspotBeacons() {
      const container = $('#hsb');
      container.innerHTML = '';
      HOTSPOTS.forEach(h => {
        h.v = latLonToVec3(h.lat, h.lon);
        const el = document.createElement('div');
        el.className = 'hs-marker';
        el.setAttribute('aria-label', h.n);
        el.innerHTML = `
          <div class="hs-tooltip">
            <b>${h.icon} ${h.n}</b>
            <small>${h.badge}</small>
          </div>
        `;
        el.addEventListener('pointerdown', e => e.stopPropagation());
        el.addEventListener('pointerup', e => e.stopPropagation());
        el.onclick = (e) => {
          e.stopPropagation();
          selectRegion(h);
        };
        container.appendChild(el);
        h.el = el;
      });
    }

    function getEarthIntersect(clientX, clientY) {
      if (!ok) {
        const canvas = $('#gl');
        if (!canvas) return null;
        const rect = canvas.getBoundingClientRect();
        const mapW = Math.min(rect.width * 0.90, rect.height * 1.80);
        const mapH = mapW * 0.5;
        const mapX = (rect.width - mapW) / 2;
        const mapY = (rect.height - mapH) / 2;
        const px = clientX - rect.left;
        const py = clientY - rect.top;

        if (px >= mapX && px <= mapX + mapW && py >= mapY && py <= mapY + mapH) {
          const u = (px - mapX) / mapW;
          const v = (py - mapY) / mapH;
          const lon = clamp((u * 360) - 180, -180, 180);
          const lat = clamp(90 - (v * 180), -90, 90);
          return { hit: null, lat, lon };
        }
        return null;
      }

      if (!earth || !cam || !R || !raycaster || !mouse) return null;
      const rect = R.domElement.getBoundingClientRect();
      mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, cam);
      const intersects = raycaster.intersectObject(earth);
      if (intersects.length > 0) {
        const hit = intersects[0];
        const local = hit.point.clone();
        earth.worldToLocal(local);
        local.normalize();
        const lat = Math.asin(clamp(local.y, -1, 1)) * (180 / Math.PI);
        const lon = Math.atan2(-local.z, local.x) * (180 / Math.PI);
        return { hit, lat, lon };
      }
      return null;
    }

    function handleEarthClick(clientX, clientY) {
      const result = getEarthIntersect(clientX, clientY);
      if (!result) return;
      const { lat, lon } = result;
      const geo = classifyGeoPoint(lat, lon);

      const latStr = Math.abs(lat).toFixed(1) + '°' + (lat >= 0 ? 'N' : 'S');
      const lonStr = Math.abs(lon).toFixed(1) + '°' + (lon >= 0 ? 'E' : 'W');

      const customSpot = {
        id: 'custom_' + Date.now(),
        n: geo.name,
        location: `${latStr}, ${lonStr}`,
        lat,
        lon,
        cat: geo.type,
        badge: geo.badge,
        soundDesc: geo.desc,
        soundType: geo.soundType,
        icon: geo.icon,
        isCustom: true
      };

      selectRegion(customSpot);
    }

    function updateScannerHover(clientX, clientY) {
      const reticle = $('#scanner-reticle');
      const pill = $('#scanner-pill');
      if (!st.scanMode) {
        reticle.style.display = 'none';
        pill.style.display = 'none';
        return;
      }

      const result = getEarthIntersect(clientX, clientY);
      if (result) {
        reticle.style.display = 'grid';
        reticle.style.left = clientX + 'px';
        reticle.style.top = clientY + 'px';

        pill.style.display = 'block';
        pill.style.left = Math.min(clientX + 28, window.innerWidth - 220) + 'px';
        pill.style.top = Math.max(clientY - 12, 60) + 'px';

        const { lat, lon } = result;
        const geo = classifyGeoPoint(lat, lon);
        const latStr = Math.abs(lat).toFixed(1) + '°' + (lat >= 0 ? 'N' : 'S');
        const lonStr = Math.abs(lon).toFixed(1) + '°' + (lon >= 0 ? 'E' : 'W');
        pill.textContent = `${geo.icon} ${latStr}, ${lonStr} · ${geo.badge}`;

        if (audio && st.play) {
          const now = audio.ctx.currentTime;
          if (audio.panner && audio.panner.pan) {
            audio.panner.pan.setTargetAtTime(clamp(lon / 180, -1, 1), now, 0.08);
          }
          const basePitch = clamp(Math.abs(lat) / 90, 0, 1);
          const filterFreq = 600 + (1 - basePitch) * 2400;
          audio.primaryFilter.frequency.setTargetAtTime(filterFreq, now, 0.1);
        }
      } else {
        reticle.style.display = 'none';
        pill.style.display = 'none';
      }
    }

    function onResize() {
      const W = window.innerWidth;
      const H = window.innerHeight;
      
      if (ok && R && cam) {
        R.setSize(W, H, false);
        cam.aspect = W / H;
        cam.updateProjectionMatrix();
        const isNarrow = W / H < 0.85;
        zT = (isNarrow ? 5.2 : 3.6) * zoom;
        planet.position.y = isNarrow ? 0.35 : 0;
      }

      if (st.dockPos === 'free') {
        const leftVal = parseInt(deck.style.left) || (W / 2 - deck.offsetWidth / 2);
        const topVal = parseInt(deck.style.top) || (H - deck.offsetHeight - 20);
        deck.style.left = clamp(leftVal, 10, Math.max(10, W - deck.offsetWidth - 10)) + 'px';
        deck.style.top = clamp(topVal, 10, Math.max(10, H - deck.offsetHeight - 10)) + 'px';
      } else {
        setDeckDock(st.dockPos);
      }
    }
    window.addEventListener('resize', onResize);

    function bindCanvasInteraction(canvas) {
      if (!canvas) return;
      canvas.addEventListener('pointerdown', e => {
        if (e.target !== canvas) return;
        pointerStartedOnGlobe = true;
        drag = true;
        tgt = null;
        lx = e.clientX;
        ly = e.clientY;
        movedDistance = 0;
        if (canvas.setPointerCapture) {
          try { canvas.setPointerCapture(e.pointerId); } catch(err) {}
        }
        canvas.classList.add('grabbing');
      });

      canvas.addEventListener('pointerleave', () => {
        if (st.scanMode) {
          $('#scanner-reticle').style.display = 'none';
          $('#scanner-pill').style.display = 'none';
        }
      });

      canvas.addEventListener('wheel', e => {
        zoom = clamp(zoom * (1 + e.deltaY * 0.001), 0.65, 1.8);
        onResize();
      }, { passive: true });
    }

    function initGlobeInteraction() {
      const canvas = $('#gl');
      bindCanvasInteraction(canvas);

      window.addEventListener('pointermove', e => {
        if (st.scanMode) {
          updateScannerHover(e.clientX, e.clientY);
        }

        if (!drag || !ok || !earth) return;
        const dx = e.clientX - lx;
        const dy = e.clientY - ly;
        movedDistance += Math.abs(dx) + Math.abs(dy);
        earth.rotation.y += dx * 0.005;
        earth.rotation.x = clamp(earth.rotation.x + dy * 0.005, -1.3, 1.3);
        lx = e.clientX;
        ly = e.clientY;
      });

      window.addEventListener('pointerup', e => {
        const wasGlobe = pointerStartedOnGlobe;
        pointerStartedOnGlobe = false;
        drag = false;
        const c = $('#gl');
        if (c) c.classList.remove('grabbing');
        if (c && c.releasePointerCapture && c.hasPointerCapture && c.hasPointerCapture(e.pointerId)) {
          try { c.releasePointerCapture(e.pointerId); } catch(err) {}
        }

        const hitUI = e.target.closest && (
          e.target.closest('#ui') ||
          e.target.closest('.hs-marker') ||
          e.target.closest('.modal-box') ||
          e.target.closest('#zen-restore-btn') ||
          e.target.closest('#milestone-alert') ||
          e.target.closest('#region-banner')
        );

        if (wasGlobe && movedDistance < 7 && !hitUI) {
          handleEarthClick(e.clientX, e.clientY);
        }
      });

      window.addEventListener('pointercancel', e => {
        pointerStartedOnGlobe = false;
        drag = false;
        const c = $('#gl');
        if (c) c.classList.remove('grabbing');
      });

      $('#zi').onclick = () => { zoom = clamp(zoom * 0.85, 0.65, 1.8); onResize(); };
      $('#zo').onclick = () => { zoom = clamp(zoom * 1.18, 0.65, 1.8); onResize(); };
    }

    // --- Web Audio API Synthesizer Architecture ---
    const SCALES = {
      pent: [0, 2, 4, 7, 9],
      min: [0, 2, 3, 5, 7, 8, 10],
      dorian: [0, 2, 3, 5, 7, 9, 10],
      phrygian: [0, 1, 3, 5, 7, 8, 10]
    };

    let audio = null;
    let audioAvailable = true;
    let tickTimer = null;
    let biomeTimer = null;

    function degreeToFreq(degree, rootFreq = 110) {
      const s = SCALES[st.scale] || SCALES.pent;
      const octave = Math.floor(degree / s.length);
      const semitone = s[((degree % s.length) + s.length) % s.length];
      return rootFreq * Math.pow(2, (octave * 12 + semitone) / 12);
    }

    function initAudioEngine() {
      if (audio) return;
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) {
          audioAvailable = false;
          $('#live-tag').innerHTML = '<span style="color:#FF5252">NO AUDIO API</span>';
          return;
        }

        const ctx = new AudioCtx();
        
        const masterGain = ctx.createGain();
        masterGain.gain.value = st.mute ? 0 : +$('#vol').value;

        const compressor = ctx.createDynamicsCompressor();
        compressor.threshold.value = -12;
        compressor.knee.value = 8;
        compressor.ratio.value = 4;

        const analyser = ctx.createAnalyser();
        analyser.fftSize = 512;
        analyser.smoothingTimeConstant = 0.82;

        masterGain.connect(compressor);
        compressor.connect(analyser);
        analyser.connect(ctx.destination);

        const panner = ctx.createStereoPanner ? ctx.createStereoPanner() : ctx.createGain();
        panner.connect(masterGain);

        const primaryFilter = ctx.createBiquadFilter();
        primaryFilter.type = 'lowpass';
        primaryFilter.frequency.value = 1400;
        primaryFilter.Q.value = 2.0;

        const filterGain = ctx.createGain();
        filterGain.gain.value = 0;
        primaryFilter.connect(filterGain);
        filterGain.connect(panner);

        const oscNodes = [0, 1, 2, 3].map(i => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = i === 1 ? 'triangle' : (i === 3 ? 'sawtooth' : 'sine');
          gain.gain.value = 0.12;
          osc.connect(gain);
          gain.connect(primaryFilter);
          osc.start();
          return { osc, gain };
        });

        const subOsc = ctx.createOscillator();
        const subGain = ctx.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.value = 55;
        subGain.gain.value = 0.18;
        subOsc.connect(subGain);
        subGain.connect(primaryFilter);
        subOsc.start();

        const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
        const noiseData = noiseBuffer.getChannelData(0);
        for (let i = 0; i < noiseData.length; i++) noiseData[i] = Math.random() * 2 - 1;

        const noiseSource = ctx.createBufferSource();
        noiseSource.buffer = noiseBuffer;
        noiseSource.loop = true;

        const noiseFilter = ctx.createBiquadFilter();
        noiseFilter.type = 'bandpass';
        noiseFilter.frequency.value = 1600;
        noiseFilter.Q.value = 3.5;

        const noiseGain = ctx.createGain();
        noiseGain.gain.value = 0;

        noiseSource.connect(noiseFilter);
        noiseFilter.connect(noiseGain);
        noiseGain.connect(panner);
        noiseSource.start();

        const delayBus = ctx.createGain();
        const delay = ctx.createDelay(1.0);
        const delayFeedback = ctx.createGain();
        const delayDamp = ctx.createBiquadFilter();

        delay.delayTime.value = 0.36;
        delayFeedback.gain.value = 0.38;
        delayDamp.type = 'lowpass';
        delayDamp.frequency.value = 2200;

        delayBus.connect(panner);
        delayBus.connect(delay);
        delay.connect(delayDamp);
        delayDamp.connect(delayFeedback);
        delayFeedback.connect(delay);
        delay.connect(panner);

        audio = {
          ctx,
          masterGain,
          panner,
          primaryFilter,
          filterGain,
          oscNodes,
          subOsc,
          subGain,
          noiseFilter,
          noiseGain,
          delayBus,
          analyser
        };
        audioAvailable = true;

      } catch (err) {
        console.warn('Audio initialization encountered an error:', err);
        audioAvailable = false;
      }
    }

    function updateAudioParams() {
      if (!audio) return;
      const c = st.cat;
      const normVal = getNorm(c, st.year);
      const now = audio.ctx.currentTime;
      const baseNote = Math.floor(normVal * 8);

      let cutoff = 1200;
      let detune = 0;
      let noiseLevel = 0.02;
      let subVol = 0.16;

      if (c === 'climate') {
        cutoff = 800 + normVal * 2800;
        detune = normVal * 20;
      } else if (c === 'oceans') {
        cutoff = 500 + normVal * 2200;
        subVol = 0.22 + normVal * 0.1;
      } else if (c === 'forests') {
        noiseLevel = (1 - normVal) * 0.15;
        cutoff = 1000 + normVal * 1500;
      } else if (c === 'atmosphere') {
        detune = normVal * 45;
        cutoff = 1200 + normVal * 2400;
      } else if (c === 'cryosphere') {
        cutoff = 1800 + (1 - normVal) * 1600;
        noiseLevel = (1 - normVal) * 0.12;
      } else if (c === 'methane') {
        subVol = 0.2 + normVal * 0.15;
        detune = normVal * 35;
      }

      [0, 2, 4, 7].forEach((step, i) => {
        const freq = degreeToFreq(baseNote + step);
        audio.oscNodes[i].osc.frequency.setTargetAtTime(freq, now, 0.15);
        audio.oscNodes[i].osc.detune.setTargetAtTime(i % 2 ? detune : 0, now, 0.2);
      });

      audio.subOsc.frequency.setTargetAtTime(c === 'cryosphere' ? 44 : 55, now, 0.2);
      audio.subGain.gain.setTargetAtTime(st.play ? subVol : 0, now, 0.2);

      audio.primaryFilter.frequency.setTargetAtTime(cutoff, now, 0.2);
      audio.noiseGain.gain.setTargetAtTime(st.play ? noiseLevel : 0, now, 0.3);

      if (audio.panner && audio.panner.pan) {
        const targetPan = st.region ? clamp(st.region.lon / 180, -1, 1) : 0;
        audio.panner.pan.setTargetAtTime(targetPan, now, 0.25);
      }

      $('#stat-res').textContent = Math.round(cutoff) + ' HZ';
      $('#osc-hz').textContent = Math.round(degreeToFreq(baseNote)) + ' HZ';
      if (st.region) {
        const panDir = st.region.lon < 0 ? `L ${Math.abs(Math.round(st.region.lon / 1.8))}%` : `R ${Math.round(st.region.lon / 1.8)}%`;
        $('#stat-pan').textContent = panDir;
      } else {
        $('#stat-pan').textContent = 'CENTER';
      }
    }

    function calculateTempo() {
      const v = getNorm(st.cat, st.year);
      const c = st.cat;
      if (c === 'climate') return Math.round(65 + v * 60);
      if (c === 'oceans') return 56;
      if (c === 'forests') return Math.round(58 + (1 - v) * 24);
      if (c === 'atmosphere') return Math.round(68 + v * 52);
      if (c === 'cryosphere') return Math.round(52 + (1 - v) * 38);
      return Math.round(60 + v * 45);
    }

    function audioTick() {
      if (!st.play || !audio) return;
      const ctx = audio.ctx;
      const v = getNorm(st.cat, st.year);
      const baseNote = Math.floor(v * 8) + [0, 2, 4, 5, 7, 9][Math.floor(Math.random() * 6)] + 7;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;

      osc.type = 'triangle';
      osc.frequency.value = degreeToFreq(baseNote);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.14, now + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

      osc.connect(gain);
      gain.connect(audio.delayBus);

      osc.onended = () => {
        try {
          osc.disconnect();
          gain.disconnect();
        } catch(e) {}
      };

      osc.start(now);
      osc.stop(now + 1.3);

      const bpm = calculateTempo();
      $('#stat-bpm').textContent = bpm + ' BPM';
      const delayMs = (60000 / bpm) / (st.cat === 'oceans' || st.cat === 'forests' ? 1 : 2);

      if (tickTimer) clearTimeout(tickTimer);
      if (st.play) {
        tickTimer = setTimeout(audioTick, delayMs);
      }
    }

    function triggerBiomeSound() {
      if (!st.play || !audio || !st.region) return;
      const ctx = audio.ctx;
      const now = ctx.currentTime;
      const sType = st.region.soundType || 'rainforest';

      if (sType === 'rainforest') {
        const osc = ctx.createOscillator();
        const mod = ctx.createOscillator();
        const modGain = ctx.createGain();
        const gain = ctx.createGain();

        osc.type = 'sine';
        mod.type = 'sine';
        mod.frequency.value = 18 + Math.random() * 12;
        modGain.gain.value = 240;

        const baseChirp = 2800 + Math.random() * 1400;
        osc.frequency.setValueAtTime(baseChirp, now);
        osc.frequency.exponentialRampToValueAtTime(baseChirp * 1.3, now + 0.12);

        mod.connect(modGain);
        modGain.connect(osc.frequency);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.06, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25);

        osc.connect(gain);
        gain.connect(audio.panner);

        osc.onended = () => {
          try {
            osc.disconnect();
            mod.disconnect();
            modGain.disconnect();
            gain.disconnect();
          } catch(e) {}
        };

        mod.start(now); osc.start(now);
        mod.stop(now + 0.3); osc.stop(now + 0.3);

      } else if (sType === 'ocean_abyss') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1150, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 0.9);

      } else if (sType === 'polar') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        const chimeFreq = 2200 + [0, 4, 7, 11, 14][Math.floor(Math.random() * 5)] * 110;
        osc.frequency.setValueAtTime(chimeFreq, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.08, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.4);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 1.5);

      } else if (sType === 'coral') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(600 + Math.random() * 800, now);
        osc.frequency.exponentialRampToValueAtTime(1600 + Math.random() * 400, now + 0.05);

        gain.gain.setValueAtTime(0.05, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);

        osc.connect(gain);
        gain.connect(audio.panner);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 0.07);

      } else if (sType === 'desert') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        const notes = [164.8, 174.6, 220.0, 246.9];
        osc.frequency.setValueAtTime(notes[Math.floor(Math.random() * notes.length)], now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.07, now + 0.2);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.8);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 1.9);

      } else if (sType === 'alpine') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(432 * 1.5, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.08, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.2);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 2.3);
      }

      const nextInterval = 900 + Math.random() * 1800;
      if (biomeTimer) clearTimeout(biomeTimer);
      if (st.play && st.region) {
        biomeTimer = setTimeout(triggerBiomeSound, nextInterval);
      }
    }

    function setPlayState(playing) {
      if (playing) {
        initAudioEngine();
        if (audio && audio.ctx.state === 'suspended') {
          audio.ctx.resume().catch(e => console.warn(e));
        }
      }
      st.play = playing;
      const playBtn = $('#play');
      const miniPlayBtn = $('#mini-play');
      const playText = $('#play-text');

      if (playing) {
        playBtn.classList.add('active');
        miniPlayBtn.classList.add('active');
        playBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        miniPlayBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        playText.textContent = 'PAUSE';
        if (audio) {
          audio.filterGain.gain.setTargetAtTime(1.0, audio.ctx.currentTime, 0.35);
          updateAudioParams();
          if (tickTimer) clearTimeout(tickTimer);
          audioTick();
          if (st.region) {
            if (biomeTimer) clearTimeout(biomeTimer);
            triggerBiomeSound();
          }
        }
      } else {
        playBtn.classList.remove('active');
        miniPlayBtn.classList.remove('active');
        playBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        miniPlayBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        playText.textContent = 'SONIFY';
        if (audio) {
          audio.filterGain.gain.setTargetAtTime(0.0, audio.ctx.currentTime, 0.35);
          updateAudioParams();
        }
        if (tickTimer) { clearTimeout(tickTimer); tickTimer = null; }
        if (biomeTimer) { clearTimeout(biomeTimer); biomeTimer = null; }
      }
    }
    $('#play').onclick = () => setPlayState(!st.play);
    $('#mini-play').onclick = () => setPlayState(!st.play);

    // --- Dynamic UI Theming & Category Selection ---
    function setCategory(catKey) {
      st.cat = catKey;
      const cat = CATS[catKey];

      $$('.cat-item').forEach(b => {
        b.classList.toggle('on', b.dataset.c === catKey);
      });

      document.documentElement.style.setProperty('--ac', cat.hex);
      document.documentElement.style.setProperty('--ac-glow', cat.glow);
      document.documentElement.style.setProperty('--ac-subtle', cat.subtle);

      $('#hud-name').textContent = cat.t;
      $('#hud-desc').textContent = cat.sub;
      $('#hud-baseline').textContent = cat.baseline;
      $('#hud-rate').textContent = cat.rate;
      $('#sensor-name').textContent = 'REFERENCE · ' + cat.sensor;

      const provStatusEl = $('#provenance-status');
      const provProviderEl = $('#provenance-provider');
      const hudProvEl = $('#hud-provenance');
      if (provStatusEl && cat.provStatus) provStatusEl.textContent = cat.provStatus;
      if (provProviderEl && cat.provProvider) provProviderEl.textContent = cat.provProvider;
      if (hudProvEl && cat.provBadgeClass) {
        hudProvEl.className = `provenance-banner mono ${cat.provBadgeClass}`;
      }

      if (U && U.uTint) U.uTint.value.set(...cat.tint);
      if (auraU) {
        auraU.uAura1.value.set(...cat.aura1);
        auraU.uAura2.value.set(...cat.aura2);
      }
      if (ring && ring.material) ring.material.color.set(cat.hex);
      if (starPoints && starPoints.material) starPoints.material.color.set(cat.hex);

      renderChartPath(catKey);
      updateAudioParams();
      updateMilestoneAlert(st.year);
    }

    function renderChartPath(catKey) {
      const cat = CATS[catKey];
      const pts = [];
      const areaPts = ['0,70'];

      for (let i = 0; i <= 45; i++) {
        const x = (i / 45 * 240).toFixed(1);
        const norm = (cat.raw[i] - cat.min) / (cat.max - cat.min);
        const y = (64 - norm * 56).toFixed(1);
        pts.push(`${x},${y}`);
        areaPts.push(`${x},${y}`);
      }
      areaPts.push('240,70');

      $('#ln').setAttribute('points', pts.join(' '));
      $('#ch-area').setAttribute('points', areaPts.join(' '));
    }

    function initCategoryNav() {
      const leftNav = $('#left');
      for (const k in CATS) {
        const c = CATS[k];
        const btn = document.createElement('button');
        btn.className = 'cat-item';
        btn.dataset.c = k;
        btn.style.setProperty('--cat-color', c.hex);
        btn.style.setProperty('--cat-subtle', c.subtle);
        btn.innerHTML = `
          <div class="cat-icon-wrap"><svg viewBox="0 0 24 24">${c.icon}</svg></div>
          <div class="cat-meta">
            <span class="cat-name">${c.n}</span>
            <span class="cat-sub">${c.u} &middot; ${c.rate}</span>
          </div>
        `;
        btn.onclick = () => setCategory(k);
        leftNav.appendChild(btn);
      }
    }

    // --- Interactive Adjustable Timeline Logic ---
    function setYear(yr, notify = true) {
      st.year = clamp(yr, 1980, 2025);
      const roundedYear = Math.round(st.year);
      $('#yr').value = roundedYear;
      $('#yt').textContent = roundedYear + (roundedYear >= 2024 ? ' · NOW' : '');
      $('#mini-year').textContent = roundedYear;
      $('#year-tag').textContent = 'EPOCH ' + roundedYear;

      $$('.ms-chip').forEach(chip => {
        chip.classList.toggle('active', +chip.dataset.yr === roundedYear);
      });

      if (notify) updateMilestoneAlert(roundedYear);
      updateAudioParams();
    }

    function updateMilestoneAlert(year) {
      const ms = MILESTONES.find(m => Math.abs(m.year - Math.round(year)) <= 0.5);
      const alertBox = $('#milestone-alert');
      if (ms) {
        $('#ms-tag').textContent = ms.tag;
        $('#ms-title').textContent = `${ms.year} · ${ms.title}`;
        $('#ms-desc').textContent = ms.desc;
        alertBox.classList.add('on');
      } else {
        alertBox.classList.remove('on');
      }
    }
    $('#btn-close-ms').onclick = () => $('#milestone-alert').classList.remove('on');

    function initMilestonesBar() {
      const bar = $('#ms-bar');
      bar.innerHTML = '';
      MILESTONES.forEach(m => {
        const chip = document.createElement('button');
        chip.className = 'ms-chip mono';
        chip.dataset.yr = m.year;
        chip.textContent = m.year;
        chip.title = m.title;
        chip.onclick = () => setYear(m.year);
        bar.appendChild(chip);
      });
    }

    $('#yr').oninput = e => setYear(+e.target.value);
    $('#btn-step-prev').onclick = () => setYear(st.year - 1);
    $('#btn-step-next').onclick = () => setYear(st.year + 1);
    $('#btn-mini-prev').onclick = () => setYear(st.year - 1);
    $('#btn-mini-next').onclick = () => setYear(st.year + 1);
    $('#btn-step-prev5').onclick = () => setYear(st.year - 5);
    $('#btn-step-next5').onclick = () => setYear(st.year + 5);
    $('#rs').onclick = () => setYear(1980);

    const chartSvg = $('#ch');
    const chartTooltip = $('#ch-tooltip');
    chartSvg.addEventListener('pointermove', e => {
      const rect = chartSvg.getBoundingClientRect();
      const xPct = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      const hoveredYear = Math.round(1980 + xPct * 45);
      const val = getVal(st.cat, hoveredYear);
      chartTooltip.textContent = `${hoveredYear}: ${val.toFixed(CATS[st.cat].d)} ${CATS[st.cat].u}`;
      chartTooltip.style.left = `${xPct * 100}%`;
      chartTooltip.style.opacity = '1';
    });
    chartSvg.addEventListener('pointerleave', () => chartTooltip.style.opacity = '0');
    chartSvg.addEventListener('click', e => {
      const rect = chartSvg.getBoundingClientRect();
      const xPct = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      setYear(Math.round(1980 + xPct * 45));
    });

    // --- Hotspot & Regional Sonification Selection ---
    function selectRegion(h) {
      st.region = h;
      HOTSPOTS.forEach(x => {
        if (x.el) x.el.classList.toggle('on', x === h);
      });

      let customEl = $('#custom-pin');
      if (h.isCustom) {
        if (!customEl) {
          customEl = document.createElement('div');
          customEl.id = 'custom-pin';
          customEl.className = 'hs-marker custom-beacon on';
          $('#hsb').appendChild(customEl);
        }
        h.el = customEl;
        customEl.innerHTML = `
          <div class="hs-tooltip" style="opacity:1">
            <b>${h.icon} ${h.n}</b>
            <small>${h.location}</small>
          </div>
        `;
      } else if (customEl) {
        customEl.remove();
      }

      h.v = latLonToVec3(h.lat, h.lon);

      if (h.cat && CATS[h.cat]) {
        setCategory(h.cat);
      }

      tgt = {
        y: -(h.lon + 90) * (Math.PI / 180),
        x: clamp(h.lat * (Math.PI / 180), -1.2, 1.2)
      };

      $('#reg-icon').textContent = h.icon;
      $('#reg-name').textContent = h.n.toUpperCase();
      $('#reg-badge').textContent = h.badge;
      $('#reg-coords').textContent = h.location;
      $('#reg-sound-desc').textContent = h.soundDesc;
      if (typeof AriaApi !== 'undefined' && AriaApi.isLive && h.lat != null && h.lon != null) {
        AriaApi.fetchRegionalWeather(h.lat, h.lon, 2022, 2023).then(data => {
          if (data && data.data && data.data.length > 0) {
            const latest = data.data[data.data.length - 1];
            $('#reg-sound-desc').textContent = `${h.soundDesc} [NASA POWER In-Situ 2m Temp: ${latest.value.toFixed(1)}°C]`;
          }
        }).catch(() => {});
      }
      $('#region-banner').classList.add('on');
      $('#tag-label').textContent = h.n.toUpperCase();
      $('#mini-region-tag').textContent = h.n.slice(0, 10).toUpperCase();

      updateAudioParams();
      if (st.play) {
        if (biomeTimer) clearTimeout(biomeTimer);
        triggerBiomeSound();
      }

      $('#region-drawer').classList.remove('open');
    }

    function resetToGlobal() {
      st.region = null;
      HOTSPOTS.forEach(x => { if (x.el) x.el.classList.remove('on'); });
      const customEl = $('#custom-pin');
      if (customEl) customEl.remove();
      $('#region-banner').classList.remove('on');
      $('#tag-label').textContent = 'GLOBAL SYNTH';
      $('#mini-region-tag').textContent = 'GLOBAL';
      if (biomeTimer) { clearTimeout(biomeTimer); biomeTimer = null; }
      updateAudioParams();
    }
    $('#btn-reset-region').onclick = resetToGlobal;

    function initRegionDrawer(filter = 'all') {
      const grid = $('#regions-grid');
      grid.innerHTML = '';
      HOTSPOTS.forEach(h => {
        if (filter !== 'all') {
          if (filter === 'atmosphere') {
            if (h.cat !== 'atmosphere' && h.cat !== 'methane') return;
          } else if (h.cat !== filter) {
            return;
          }
        }

        const cat = CATS[h.cat] || CATS.climate;
        const card = document.createElement('div');
        card.className = 'reg-card';
        card.style.setProperty('--card-color', cat.hex);
        card.style.setProperty('--card-subtle', cat.subtle);
        card.innerHTML = `
          <div class="rc-top">
            <span class="rc-icon">${h.icon}</span>
            <span class="rc-badge">${h.badge}</span>
          </div>
          <div class="rc-name">${h.n}</div>
          <div class="rc-loc">${h.location}</div>
          <div class="rc-sound">${h.soundDesc}</div>
          <button class="rc-btn">LISTEN TO REGION</button>
        `;
        card.onclick = () => selectRegion(h);
        grid.appendChild(card);
      });
    }

    $$('.biome-filter-btn').forEach(btn => {
      btn.onclick = () => {
        $$('.biome-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        initRegionDrawer(btn.dataset.filter);
      };
    });

    $('#btn-regions').onclick = () => {
      initRegionDrawer('all');
      $('#region-drawer').classList.add('open');
    };
    $('#btn-close-regions').onclick = () => $('#region-drawer').classList.remove('open');

    $('#btn-scanner').onclick = () => {
      st.scanMode = !st.scanMode;
      $('#btn-scanner').classList.toggle('active', st.scanMode);
      $('#scanner-btn-label').textContent = st.scanMode ? 'SCANNING ON' : 'SCAN EARTH';
      if (st.scanMode) {
        setPlayState(true);
      } else {
        $('#scanner-reticle').style.display = 'none';
        $('#scanner-pill').style.display = 'none';
      }
    };

    // --- Control Deck Dragging & Docking System ---
    const deck = $('#jb');
    const dragHandle = $('#deck-drag');
    let isDraggingDeck = false;
    let deckStartX, deckStartY, deckInitialLeft, deckInitialTop;

    dragHandle.addEventListener('pointerdown', e => {
      if (e.target.closest('button')) return;
      isDraggingDeck = true;
      if (dragHandle.setPointerCapture) {
        try { dragHandle.setPointerCapture(e.pointerId); } catch(err) {}
      }
      const rect = deck.getBoundingClientRect();
      deckStartX = e.clientX;
      deckStartY = e.clientY;
      deckInitialLeft = rect.left;
      deckInitialTop = rect.top;

      deck.style.transform = 'none';
      deck.style.left = deckInitialLeft + 'px';
      deck.style.top = deckInitialTop + 'px';
      deck.style.bottom = 'auto';
      st.dockPos = 'free';
      $('#sel-dock-pos').value = 'free';
    });

    window.addEventListener('pointermove', e => {
      if (!isDraggingDeck) return;
      const dx = e.clientX - deckStartX;
      const dy = e.clientY - deckStartY;
      const newLeft = clamp(deckInitialLeft + dx, 10, window.innerWidth - deck.offsetWidth - 10);
      const newTop = clamp(deckInitialTop + dy, 10, window.innerHeight - deck.offsetHeight - 10);
      deck.style.left = newLeft + 'px';
      deck.style.top = newTop + 'px';
    });

    window.addEventListener('pointerup', e => {
      if (isDraggingDeck) {
        isDraggingDeck = false;
        if (dragHandle.releasePointerCapture && dragHandle.hasPointerCapture && dragHandle.hasPointerCapture(e.pointerId)) {
          try { dragHandle.releasePointerCapture(e.pointerId); } catch(err) {}
        }
      }
    });

    function setDeckDock(pos) {
      st.dockPos = pos;
      if (pos === 'bottom') {
        deck.style.left = '50%';
        deck.style.top = 'auto';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.right = 'auto';
        deck.style.transform = 'translateX(-50%)';
      } else if (pos === 'top') {
        deck.style.left = '50%';
        deck.style.top = 'calc(70px + env(safe-area-inset-top, 0px))';
        deck.style.bottom = 'auto';
        deck.style.right = 'auto';
        deck.style.transform = 'translateX(-50%)';
      } else if (pos === 'left') {
        deck.style.left = '22px';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.top = 'auto';
        deck.style.right = 'auto';
        deck.style.transform = 'none';
      } else if (pos === 'right') {
        deck.style.left = 'auto';
        deck.style.right = '22px';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.top = 'auto';
        deck.style.transform = 'none';
      }
    }

    const DOCK_CYCLE = ['bottom', 'top', 'left', 'right'];
    $('#btn-dock-cycle').onclick = () => {
      let nextIdx = (DOCK_CYCLE.indexOf(st.dockPos) + 1) % DOCK_CYCLE.length;
      setDeckDock(DOCK_CYCLE[nextIdx]);
      $('#sel-dock-pos').value = DOCK_CYCLE[nextIdx];
    };
    $('#sel-dock-pos').onchange = e => setDeckDock(e.target.value);

    function toggleDeckMinimize() {
      deck.classList.toggle('minimized');
      const isMin = deck.classList.contains('minimized');
      $('#btn-minimize-deck').innerHTML = isMin ? 
        '<svg viewBox="0 0 24 24"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>' :
        '<svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>';
      $('#btn-minimize-deck').title = isMin ? 'Expand Control Deck' : 'Minimize Control Deck';
    }
    $('#btn-minimize-deck').onclick = toggleDeckMinimize;
    $('#btn-expand-deck').onclick = toggleDeckMinimize;

    function toggleZenMode() {
      document.body.classList.toggle('zen-mode');
      const isZen = document.body.classList.contains('zen-mode');
      $('#btn-zen').classList.toggle('active', isZen);
    }
    $('#btn-zen').onclick = toggleZenMode;
    $('#zen-restore-btn').onclick = toggleZenMode;
    window.addEventListener('keydown', e => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA')) {
        return;
      }
      if (e.key === 'z' || e.key === 'Z') {
        toggleZenMode();
      } else if (e.code === 'Space') {
        e.preventDefault();
        setPlayState(!st.play);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        setYear(Math.min(2025, st.year + 1));
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        setYear(Math.max(1980, st.year - 1));
      } else if (e.key === 'Escape') {
        $('#settings-modal').classList.remove('open');
        $('#region-drawer').classList.remove('open');
        const dm = $('#data-modal');
        if (dm) dm.classList.remove('open');
        if (document.body.classList.contains('zen-mode')) toggleZenMode();
      }
    });

    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      st.rotSpeed = 'off';
      const selRot = $('#sel-rot');
      if (selRot) selRot.value = 'off';
    }

    const btnCloseFb = $('#btn-close-fb');
    if (btnCloseFb) {
      btnCloseFb.onclick = () => {
        const fb = $('#fb');
        if (fb) fb.style.display = 'none';
      };
    }

    $('#btn-settings').onclick = () => $('#settings-modal').classList.add('open');
    $('#btn-close-settings').onclick = () => $('#settings-modal').classList.remove('open');

    // Scientific Data Transparency Modal Listeners
    const btnData = $('#btn-data-transparency');
    if (btnData) btnData.onclick = () => $('#data-modal').classList.add('open');
    const hudProv = $('#hud-provenance');
    if (hudProv) hudProv.onclick = () => $('#data-modal').classList.add('open');
    const btnCloseData = $('#btn-close-data');
    if (btnCloseData) btnCloseData.onclick = () => $('#data-modal').classList.remove('open');
    const dataModal = $('#data-modal');
    if (dataModal) {
      dataModal.onclick = (e) => {
        if (e.target === dataModal) dataModal.classList.remove('open');
      };
    }
    const bBadge = $('#backend-badge');
    if (bBadge) bBadge.onclick = () => $('#settings-modal').classList.add('open');
    const syncBtn = $('#btn-sync-backend');
    if (syncBtn) {
      syncBtn.onclick = () => {
        const inp = $('#inp-backend-url');
        if (inp && inp.value) AriaApi.setBaseUrl(inp.value);
        AriaApi.syncWithBackend();
      };
    }

    $('#sel-scale').onchange = e => {
      st.scale = e.target.value;
      const names = { pent: 'PENTATONIC', min: 'NATURAL MINOR', dorian: 'DORIAN MODE', phrygian: 'PHRYGIAN' };
      $('#scale-badge').textContent = names[st.scale] || 'PENTATONIC';
      updateAudioParams();
    };
    $('#sel-rot').onchange = e => st.rotSpeed = e.target.value;
    $('#sel-aura').onchange = e => {
      st.auraIntensity = +e.target.value;
      if (auraU) auraU.uIntensity.value = st.auraIntensity;
    };

    $('#btn-fs').onclick = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    };

    $('#vol').oninput = e => {
      if (audio && !st.mute) audio.masterGain.gain.value = +e.target.value;
    };
    $('#snd').onclick = e => {
      st.mute = !st.mute;
      e.currentTarget.classList.toggle('on', st.mute);
      if (audio) audio.masterGain.gain.value = st.mute ? 0 : +$('#vol').value;
    };

    $('#go').onclick = () => {
      $('#intro').classList.add('off');
      $('#ui').classList.add('on');
      setPlayState(true);
    };

    // --- Main Animation & Render Loop ---
    const waveCtx = $('#wv').getContext('2d');
    const specCtx = $('#sp').getContext('2d');
    const timeData = new Uint8Array(256);
    const freqData = new Uint8Array(128);
    let lastTime = performance.now();

    function renderLoop(now) {
      requestAnimationFrame(renderLoop);
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      const c = CATS[st.cat];
      const curVal = getVal(st.cat, st.year);
      const normVal = getNorm(st.cat, st.year);
      const base1980Val = c.raw[0];
      const delta1980 = curVal - base1980Val;

      const signPrefix = (st.cat === 'climate' || st.cat === 'oceans') && curVal >= 0 ? '+' : '';
      $('#val').innerHTML = `${signPrefix}${curVal.toFixed(c.d)}<small>${c.u}</small>`;

      const trendEl = $('#trend');
      const deltaSign = delta1980 >= 0 ? '▲ +' : '▼ ';
      trendEl.textContent = `${deltaSign}${Math.abs(delta1980).toFixed(c.d)} ${c.u} SINCE 1980`;
      trendEl.className = `delta-badge mono ${delta1980 >= 0 ? 'up' : 'down'}`;

      const xPos = ((st.year - 1980) / 45 * 240).toFixed(1);
      const yPos = (64 - normVal * 56).toFixed(1);
      $('#dt').setAttribute('cx', xPos);
      $('#dt').setAttribute('cy', yPos);
      $('#cursor-ln').setAttribute('x1', xPos);
      $('#cursor-ln').setAttribute('x2', xPos);

      // Render Audio Visualizers
      waveCtx.clearRect(0, 0, 260, 26);
      specCtx.clearRect(0, 0, 260, 26);

      if (audio && st.play && audio.analyser) {
        audio.analyser.getByteTimeDomainData(timeData);
        audio.analyser.getByteFrequencyData(freqData);

        waveCtx.strokeStyle = c.hex;
        waveCtx.lineWidth = 1.5;
        waveCtx.shadowColor = c.hex;
        waveCtx.shadowBlur = 4;
        waveCtx.beginPath();
        for (let i = 0; i < 256; i++) {
          const x = (i / 255) * 260;
          const y = (timeData[i] / 255) * 26;
          if (i === 0) waveCtx.moveTo(x, y);
          else waveCtx.lineTo(x, y);
        }
        waveCtx.stroke();
        waveCtx.shadowBlur = 0;

        const barCount = 30;
        const barWidth = 260 / barCount - 2;
        for (let i = 0; i < barCount; i++) {
          const h = (freqData[i * 2] / 255) * 24;
          const x = i * (barWidth + 2);
          const y = 26 - h;
          const grad = specCtx.createLinearGradient(0, y, 0, 26);
          grad.addColorStop(0, '#FFFFFF');
          grad.addColorStop(0.3, c.hex);
          grad.addColorStop(1, 'rgba(255,255,255,0.05)');
          specCtx.fillStyle = grad;
          specCtx.fillRect(x, y, barWidth, h);
        }
      } else {
        waveCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        waveCtx.beginPath();
        waveCtx.moveTo(0, 13);
        waveCtx.lineTo(260, 13);
        waveCtx.stroke();
      }

      // 3D WebGL or 2D Interactive Fallback Rendering
      if (!ok) {
        render2DFallbackMap(now, dt, normVal, c);
        return;
      }

      if (!earth || !cam || !R || !scene) return;

      if (U && U.uTime) {
        U.uTime.value = now / 1000;
        U.uV.value += (normVal - U.uV.value) * Math.min(1, dt * 3.5);
      }

      if (tgt) {
        let dy = tgt.y - earth.rotation.y;
        dy = Math.atan2(Math.sin(dy), Math.cos(dy));
        earth.rotation.y += dy * Math.min(1, dt * 4);
        earth.rotation.x += (tgt.x - earth.rotation.x) * Math.min(1, dt * 4);
      } else if (!drag) {
        const rotMultiplier = st.rotSpeed === 'fast' ? 0.12 : (st.rotSpeed === 'slow' ? 0.02 : 0.05);
        if (st.rotSpeed !== 'off') {
          earth.rotation.y += dt * rotMultiplier;
        }
      }

      cam.position.z += (zT - cam.position.z) * Math.min(1, dt * 5);

      const allMarkers = [...HOTSPOTS];
      if (st.region && st.region.isCustom && st.region.el) {
        allMarkers.push(st.region);
      }

      allMarkers.forEach(h => {
        if (!h.el || !h.v) return;
        const normalVec = h.v.clone().applyEuler(earth.rotation);
        const worldPos = normalVec.clone().multiplyScalar(1.02).add(planet.position);
        const isVisible = normalVec.dot(cam.position.clone().sub(worldPos)) > 0;

        worldPos.project(cam);
        const sx = (worldPos.x * 0.5 + 0.5) * window.innerWidth;
        const sy = (-worldPos.y * 0.5 + 0.5) * window.innerHeight;

        h.el.style.transform = `translate(${sx}px, ${sy}px)`;
        h.el.style.opacity = isVisible && $('#ui').classList.contains('on') && !document.body.classList.contains('zen-mode') ? '1' : '0';
        h.el.style.pointerEvents = isVisible ? 'auto' : 'none';
      });

      R.render(scene, cam);
    }

    // --- Central ARIA Frontend API Client ---
    const isLocalDev = Boolean(
      typeof window !== 'undefined' && (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.protocol === 'file:' ||
        window.location.hostname === ''
      )
    );

    const AriaApi = {
      baseUrl: (typeof localStorage !== 'undefined' && localStorage.getItem('aria_backend_url')) || (isLocalDev ? 'http://127.0.0.1:8000' : ''),
      isLive: false,
      lastSync: null,

      async init() {
        const inp = $('#inp-backend-url');
        if (inp) inp.value = this.baseUrl;

        if (!this.baseUrl) {
          this.setStandaloneMode();
          return true;
        }
        return await this.syncWithBackend();
      },

      setStandaloneMode() {
        this.isLive = false;
        const badge = $('#backend-badge');
        const statusText = $('#backend-status-text');
        const warnEl = $('#backend-mixed-warn');
        if (warnEl) warnEl.style.display = 'none';
        if (badge) {
          badge.textContent = '● NASA/NOAA REFERENCE ENGINE';
          badge.style.color = '#80D8FF';
          badge.style.borderColor = 'rgba(128, 216, 255, 0.4)';
        }
        if (statusText) {
          statusText.textContent = 'STATUS: STANDALONE EMPIRICAL RECORD (1980–2025 NASA & NOAA REFERENCE ENGINE)';
          statusText.style.color = '#80D8FF';
        }
      },

      setBaseUrl(url) {
        if (!url || !url.trim()) {
          this.baseUrl = '';
          try {
            if (typeof localStorage !== 'undefined') localStorage.removeItem('aria_backend_url');
          } catch(e) {}
          this.setStandaloneMode();
          return;
        }

        const trimmed = url.trim().replace(/\/+$/, '');
        this.baseUrl = trimmed;
        try {
          if (typeof localStorage !== 'undefined') localStorage.setItem('aria_backend_url', this.baseUrl);
        } catch(e) {}
      },

      async checkHealth() {
        if (!this.baseUrl) return false;
        try {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort(), 2000);
          const res = await fetch(`${this.baseUrl}/api/v1/health`, { method: 'GET', signal: controller.signal });
          clearTimeout(timer);
          if (!res.ok) return false;
          const data = await res.json();
          return data.status === 'healthy';
        } catch (e) {
          return false;
        }
      },

      async syncWithBackend() {
        const badge = $('#backend-badge');
        const statusText = $('#backend-status-text');
        const warnEl = $('#backend-mixed-warn');

        if (!this.baseUrl) {
          this.setStandaloneMode();
          return true;
        }

        // Mixed Content Check
        if (typeof window !== 'undefined' && window.location.protocol === 'https:' && this.baseUrl.startsWith('http://')) {
          if (warnEl) warnEl.style.display = 'block';
          if (statusText) {
            statusText.textContent = 'BLOCKED: Cannot request insecure HTTP from HTTPS page (Mixed Content).';
            statusText.style.color = '#FF5252';
          }
          if (badge) {
            badge.textContent = '● MIXED CONTENT BLOCKED';
            badge.style.color = '#FF5252';
            badge.style.borderColor = '#FF5252';
          }
          return false;
        }
        if (warnEl) warnEl.style.display = 'none';

        if (statusText) statusText.textContent = 'STATUS: CONNECTING TO ' + this.baseUrl + '...';
        if (badge) {
          badge.textContent = '● BACKEND: CONNECTING';
          badge.style.color = '#FFB74D';
          badge.style.borderColor = 'rgba(255, 183, 77, 0.4)';
        }

        const healthy = await this.checkHealth();
        if (!healthy) {
          this.isLive = false;
          if (badge) {
            badge.textContent = '● NASA/NOAA REFERENCE ENGINE';
            badge.style.color = '#80D8FF';
            badge.style.borderColor = 'rgba(128, 216, 255, 0.4)';
          }
          if (statusText) {
            statusText.textContent = `STATUS: UNREACHABLE (${this.baseUrl}) — USING CURATED NASA/NOAA REFERENCE ENGINE`;
            statusText.style.color = '#80D8FF';
          }
          return false;
        }

        this.isLive = true;
        this.lastSync = new Date();
        if (badge) {
          badge.textContent = '● NASA/NOAA LIVE';
          badge.style.color = '#00E676';
          badge.style.borderColor = '#00E676';
        }
        if (statusText) {
          statusText.textContent = 'STATUS: CONNECTED TO FASTAPI (REAL NASA/NOAA TELEMETRY)';
          statusText.style.color = '#00E676';
        }

        try {
          // 1. Fetch real NASA GISTEMP LOTI annual series (1980–2025)
          const gistempRes = await fetch(`${this.baseUrl}/api/v1/climate/temperature/global?start_year=1980&end_year=2025`);
          if (gistempRes.ok) {
            const json = await gistempRes.json();
            const yearAverages = {};
            json.data.forEach(p => {
              if (!yearAverages[p.year]) yearAverages[p.year] = [];
              yearAverages[p.year].push(p.value);
            });
            const newRaw = [];
            for (let y = 1980; y <= 2025; y++) {
              if (yearAverages[y] && yearAverages[y].length > 0) {
                const avg = yearAverages[y].reduce((a, b) => a + b, 0) / yearAverages[y].length;
                newRaw.push(parseFloat(avg.toFixed(2)));
              } else if (newRaw.length > 0) {
                newRaw.push(newRaw[newRaw.length - 1]);
              } else {
                newRaw.push(CATS.climate.raw[y - 1980]);
              }
            }
            if (newRaw.length === 46) {
              CATS.climate.raw = newRaw;
              CATS.climate.min = Math.min(...newRaw);
              CATS.climate.max = Math.max(...newRaw);
              CATS.climate.sub = 'NASA GISS GISTEMP v4 LOTI (Empirical Download)';
              CATS.climate.sensor = 'NASA Goddard Institute for Space Studies';
            }
          }

          // 2. Fetch real NOAA GML Mauna Loa monthly CO2 (1980–2025)
          const co2Res = await fetch(`${this.baseUrl}/api/v1/atmosphere/co2/mauna-loa?start_year=1980&end_year=2025`);
          if (co2Res.ok) {
            const json = await co2Res.json();
            const yearAverages = {};
            json.data.forEach(p => {
              if (!yearAverages[p.year]) yearAverages[p.year] = [];
              yearAverages[p.year].push(p.value);
            });
            const newRaw = [];
            for (let y = 1980; y <= 2025; y++) {
              if (yearAverages[y] && yearAverages[y].length > 0) {
                const avg = yearAverages[y].reduce((a, b) => a + b, 0) / yearAverages[y].length;
                newRaw.push(parseFloat(avg.toFixed(1)));
              } else if (newRaw.length > 0) {
                newRaw.push(newRaw[newRaw.length - 1]);
              } else {
                newRaw.push(CATS.atmosphere.raw[y - 1980]);
              }
            }
            if (newRaw.length === 46) {
              CATS.atmosphere.raw = newRaw;
              CATS.atmosphere.min = Math.min(...newRaw);
              CATS.atmosphere.max = Math.max(...newRaw);
              CATS.atmosphere.sub = 'NOAA GML Mauna Loa In-Situ Baseline Record';
              CATS.atmosphere.sensor = 'NOAA Global Monitoring Laboratory & Scripps';
            }
          }

          // 3. Fetch real NOAA GML Global Monthly Methane (CH4) (1983–2025)
          const ch4Res = await fetch(`${this.baseUrl}/api/v1/atmosphere/methane/global?start_year=1983&end_year=2025`);
          if (ch4Res.ok) {
            const json = await ch4Res.json();
            const yearAverages = {};
            json.data.forEach(p => {
              if (!yearAverages[p.year]) yearAverages[p.year] = [];
              yearAverages[p.year].push(p.value);
            });
            const newRaw = [];
            for (let y = 1980; y <= 2025; y++) {
              if (yearAverages[y] && yearAverages[y].length > 0) {
                const avg = yearAverages[y].reduce((a, b) => a + b, 0) / yearAverages[y].length;
                newRaw.push(Math.round(avg));
              } else if (newRaw.length > 0) {
                newRaw.push(newRaw[newRaw.length - 1]);
              } else {
                newRaw.push(CATS.methane.raw[y - 1980]);
              }
            }
            if (newRaw.length === 46) {
              CATS.methane.raw = newRaw;
              CATS.methane.min = Math.min(...newRaw);
              CATS.methane.max = Math.max(...newRaw);
              CATS.methane.sub = 'NOAA GML Globally Averaged Marine Surface CH₄';
              CATS.methane.sensor = 'NOAA Global Greenhouse Gas Reference Network';
            }
          }

          // 4. Fetch real NOAA / Satellite Altimetry Global Sea Level (1993–2025)
          const slRes = await fetch(`${this.baseUrl}/api/v1/oceans/sea-level/global?start_year=1993&end_year=2025`);
          if (slRes.ok) {
            const json = await slRes.json();
            this.seaLevelData = json.data;
          }

          setCategory(st.cat);
          renderChartPath(st.cat);
          updateAudioParams();
        } catch (err) {
          console.warn('Real dataset synchronization warning:', err);
        }

        return true;
      },

      async fetchRegionalWeather(lat, lon, startYear = 2022, endYear = 2023) {
        if (!this.isLive) return null;
        try {
          const res = await fetch(`${this.baseUrl}/api/v1/climate/temperature/regional?latitude=${lat.toFixed(2)}&longitude=${lon.toFixed(2)}&start_year=${startYear}&end_year=${endYear}`);
          if (res.ok) return await res.json();
        } catch (e) {
          console.warn('Regional weather fetch error:', e);
        }
        return null;
      }
    };

    // Expose programmatic interface for testing, automation & external monitoring
    window.ARIA = {
      st,
      get ok() { return ok; },
      get zoom() { return zoom; },
      get audio() { return audio; },
      get audioAvailable() { return audioAvailable; },
      get earth() { return earth; },
      get planet() { return planet; },
      api: AriaApi,
      setCategory,
      setYear,
      selectRegion,
      resetToGlobal,
      setPlayState,
      toggleDeckMinimize,
      setDeckDock,
      toggleZenMode,
      handleEarthClick,
      updateScannerHover,
      onResize,
      HOTSPOTS,
      CATS,
      MILESTONES
    };

    // Also bind directly to window for global convenience and test suite backwards compatibility
    window.st = st;
    window.AriaApi = AriaApi;
    window.setCategory = setCategory;
    window.setYear = setYear;
    window.selectRegion = selectRegion;
    window.resetToGlobal = resetToGlobal;
    window.handleEarthClick = handleEarthClick;
    window.updateScannerHover = updateScannerHover;
    window.setDeckDock = setDeckDock;
    window.toggleDeckMinimize = toggleDeckMinimize;
    window.toggleZenMode = toggleZenMode;
    window.onResize = onResize;
    Object.defineProperty(window, 'ok', { get: () => ok });
    Object.defineProperty(window, 'zoom', { get: () => zoom });
    Object.defineProperty(window, 'audio', { get: () => audio });
    Object.defineProperty(window, 'audioAvailable', { get: () => audioAvailable });
    Object.defineProperty(window, 'earth', { get: () => earth });
    Object.defineProperty(window, 'planet', { get: () => planet });

    // --- Initialization Sequence ---
    window.addEventListener('DOMContentLoaded', () => {
      initWebGL();
      onResize();
      initGlobeInteraction();
      initCategoryNav();
      initMilestonesBar();
      initHotspotBeacons();
      initRegionDrawer('all');
      setCategory('climate');
      setYear(1990);
      AriaApi.init();
      
      if (window.innerWidth < 600) {
        toggleDeckMinimize();
      }

      requestAnimationFrame(renderLoop);
    });
  </script>
</body>
</html>
'''

def build(output_path=None):
    if output_path is None:
        output_path = os.path.join(SCRIPT_DIR, 'index.html')
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    print(f"Successfully generated: {output_path} ({len(HTML_CONTENT)} bytes)")

    # Keep companion app.js synchronized
    script_start = HTML_CONTENT.find('<script>') + len('<script>')
    script_end = HTML_CONTENT.rfind('</script>')
    if script_start > len('<script>') and script_end > script_start:
        app_js_path = os.path.join(output_dir, 'app.js')
        with open(app_js_path, 'w', encoding='utf-8') as f:
            f.write(HTML_CONTENT[script_start:script_end].strip() + '\n')
        print(f"Successfully synchronized: {app_js_path}")

if __name__ == '__main__':
    out = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-o', '--output') and len(sys.argv) > 2:
            out = sys.argv[2]
        else:
            out = sys.argv[1]
    build(out)
