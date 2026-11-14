<?php
declare(strict_types=1);

header('Content-Type: image/svg+xml; charset=utf-8');
header('Cache-Control: public, max-age=180, s-maxage=180');
header('Access-Control-Allow-Origin: *');

$handle = preg_replace('/[^A-Za-z0-9_-]/', '', (string)($_GET['handle'] ?? 'ElNeMeR')) ?: 'ElNeMeR';
$handle = substr($handle, 0, 28);

$stack = strtolower(preg_replace('/[^A-Za-z0-9_-]/', '', (string)($_GET['stack'] ?? '')) ?: '');
$saved = isset($_GET['saved']) ? max(0, (int)$_GET['saved']) : null;
$usd = isset($_GET['usd']) ? round(max(0.0, (float)$_GET['usd']), 2) : null;
$pct = isset($_GET['pct']) ? round(max(0.0, min(99.9, (float)$_GET['pct'])), 1) : null;
$grade = preg_replace('/[^A-DF+-]/', '', strtoupper((string)($_GET['grade'] ?? ''))) ?: '';

$dbFile = __DIR__ . '/data/leaderboard.sqlite';
if (is_file($dbFile)) {
    try {
        $pdo = new PDO('sqlite:' . $dbFile);
        $stmt = $pdo->prepare("SELECT stack, tokens_saved, usd_saved, compression_pct, grade FROM leaderboard WHERE LOWER(handle) = LOWER(?) LIMIT 1");
        $stmt->execute([$handle]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row) {
            if ($stack === '') $stack = (string)$row['stack'];
            if ($saved === null) $saved = (int)$row['tokens_saved'];
            if ($usd === null) $usd = (float)$row['usd_saved'];
            if ($pct === null) $pct = (float)$row['compression_pct'];
            if ($grade === '') $grade = (string)$row['grade'];
        }
    } catch (Throwable $e) {
    }
}

if ($stack === '') $stack = 'polyglot';
if ($saved === null) $saved = 1250000;
if ($usd === null) $usd = round(($saved / 1000000.0) * 15.0, 2);
if ($pct === null) $pct = 96.8;
if ($grade === '') $grade = 'A+';

if ($saved >= 1000000) {
    $savedFmt = number_format($saved / 1000000, 2) . 'M';
} elseif ($saved >= 1000) {
    $savedFmt = number_format($saved / 1000, 1) . 'K';
} else {
    $savedFmt = (string)$saved;
}
$usdFmt = '$' . number_format($usd, 2);
$tier = $saved >= 5000000 ? 'OMNISCIENT ARCHITECT' : ($saved >= 500000 ? 'S-TIER QUOTA GUARDIAN' : 'AI EFFICIENCY PIONEER');

$hSafe = htmlspecialchars('@' . $handle, ENT_QUOTES, 'UTF-8');
$sSafe = htmlspecialchars(strtoupper($stack), ENT_QUOTES, 'UTF-8');
$gSafe = htmlspecialchars($grade, ENT_QUOTES, 'UTF-8');

echo <<<SVG
<svg xmlns="http://www.w3.org/2000/svg" width="495" height="175" viewBox="0 0 495 175" fill="none" role="img" aria-label="Smart Quota OS Trophy Card for {$hSafe}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="495" y2="175" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="55%" stop-color="#EEF2FF"/>
      <stop offset="100%" stop-color="#ECFEFF"/>
    </linearGradient>
    <linearGradient id="borderGrad" x1="0" y1="0" x2="495" y2="175" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#4F46E5"/>
      <stop offset="52%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#10B981"/>
    </linearGradient>
    <linearGradient id="pill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#4F46E5"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
  </defs>

  <rect x="1.5" y="1.5" width="492" height="172" rx="18" fill="url(#bg)" stroke="url(#borderGrad)" stroke-width="2.2"/>
  <circle cx="445" cy="28" r="70" fill="#4F46E5" fill-opacity="0.08"/>
  <circle cx="60" cy="155" r="56" fill="#0EA5E9" fill-opacity="0.09"/>

  <text x="24" y="34" fill="#4F46E5" font-family="'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif" font-size="11.5" font-weight="800" letter-spacing="1.1">⚡ SMART QUOTA OS v9.0 • {$tier}</text>
  <text x="24" y="61" fill="#0F172A" font-family="'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif" font-size="20" font-weight="800">{$hSafe}</text>

  <rect x="366" y="18" width="105" height="27" rx="13.5" fill="url(#pill)"/>
  <text x="418.5" y="35.5" text-anchor="middle" fill="#FFFFFF" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="11" font-weight="800">{$sSafe} • {$gSafe}</text>

  <rect x="24" y="78" width="142" height="62" rx="12" fill="#FFFFFF" stroke="#C7D2FE" stroke-width="1.2"/>
  <text x="36" y="98" fill="#64748B" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="10" font-weight="700">TOKENS PREVENTED</text>
  <text x="36" y="125" fill="#4F46E5" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="21" font-weight="800">{$savedFmt}</text>

  <rect x="177" y="78" width="142" height="62" rx="12" fill="#FFFFFF" stroke="#A7F3D0" stroke-width="1.2"/>
  <text x="189" y="98" fill="#64748B" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="10" font-weight="700">VERIFIED COMPRESSION</text>
  <text x="189" y="125" fill="#059669" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="21" font-weight="800">-{$pct}%</text>

  <rect x="330" y="78" width="141" height="62" rx="12" fill="#FFFFFF" stroke="#FDE68A" stroke-width="1.2"/>
  <text x="342" y="98" fill="#64748B" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="10" font-weight="700">EST. API SAVED</text>
  <text x="342" y="125" fill="#D97706" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="21" font-weight="800">{$usdFmt}</text>

  <text x="24" y="160" fill="#475569" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="10.5" font-weight="700">3-Stage Firewall • 31 Native MCP Tools • Hive-Mind Brain</text>
  <text x="471" y="160" text-anchor="end" fill="#4F46E5" font-family="'Plus Jakarta Sans', 'Segoe UI', sans-serif" font-size="10.5" font-weight="800">sqo.elnemer-ai.com</text>
</svg>
SVG;
