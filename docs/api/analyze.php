<?php
declare(strict_types=1);

/**
 * Smart Quota & Superpowers OS v12.0 Quantum — Live Cloud 6-Engine Code Doctor API
 * Endpoint: POST https://sqo.elnemer-ai.com/api/analyze.php
 * Runs Security SAST + Cloud FinOps + Council TOCTOU/SRE + N+1 Perf + RTL/UI + Karpathy/SDK checks in <8ms!
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$raw = file_get_contents('php://input') ?: '';
$body = json_decode($raw, true);
$code = is_array($body) && isset($body['code']) ? (string)$body['code'] : '';

if (strlen($code) > 65000) {
    $code = substr($code, 0, 65000);
}

$findings = [];
$secPen = 0;
$perfPen = 0;
$rtlPen = 0;
$karpPen = 0;

$lines = preg_split("/\r\n|\n|\r/", $code) ?: [];

// 1. Security SAST Checks
foreach ($lines as $i => $ln) {
    $lnNum = $i + 1;
    if (preg_match('/(?:f["\'][^"\']*\b(?:SELECT|DELETE\s+FROM|UPDATE)\b[^"\']*\{|`[^`]*\b(?:SELECT|DELETE\s+FROM)\b[^`]*\$\{)/i', $ln)) {
        $findings[] = ['pillar' => 'Security SAST', 'severity' => 'CRITICAL', 'line' => $lnNum, 'msg' => 'CWE-89 SQL Injection via string interpolation — use parameterized queries (?)'];
        $secPen += 35;
    }
    if (preg_match('/(?:\bos\.system\s*\(|shell\s*=\s*True|dangerouslySetInnerHTML|\beval\s*\()/i', $ln)) {
        $findings[] = ['pillar' => 'Security SAST', 'severity' => 'HIGH', 'line' => $lnNum, 'msg' => 'CWE-78/79/95 Dangerous Command/XSS/Eval sink — sanitize or use safe APIs'];
        $secPen += 25;
    }
    if (preg_match('/(?:\/\/|#)\s*(?:TODO|FIXME|\.\.\.\s*rest)/i', $ln) || preg_match('/UnimplementedError|NotImplementedError/', $ln)) {
        $findings[] = ['pillar' => 'Karpathy Gate', 'severity' => 'HIGH', 'line' => $lnNum, 'msg' => 'Unfinished TODO / stub placeholder violates Goal-Driven Completion law'];
        $karpPen += 25;
    }
    if (preg_match('/\b(?:EdgeInsets\.only\s*\([^)]*(?:left|right)\s*:|Alignment\.(?:centerLeft|centerRight)|margin-left\s*:|padding-right\s*:)/', $ln)) {
        $findings[] = ['pillar' => 'RTL & UI Audit', 'severity' => 'MEDIUM', 'line' => $lnNum, 'msg' => 'Hardcoded left/right breaks Arabic RTL — use EdgeInsetsDirectional / margin-inline-start'];
        $rtlPen += 20;
    }
    if (preg_match('/\bWillPopScope\s*\(|\.withOpacity\s*\(|google\.generativeai|ChatCompletion\.create/', $ln)) {
        $findings[] = ['pillar' => 'SDK Radar', 'severity' => 'MEDIUM', 'line' => $lnNum, 'msg' => 'Deprecated 2023 SDK call — upgrade to PopScope / .withValues(alpha:) / google-genai / OpenAI v1+'];
        $karpPen += 18;
    }
}

// 2. N+1 Loop & LLM FinOps Loop Check
for ($i = 0; $i < count($lines); $i++) {
    if (preg_match('/^\s*(?:for\s*\(|for\s+\w+\s+in\b|foreach\s*\(|while\s*\()/', $lines[$i])) {
        $window = implode("\n", array_slice($lines, $i + 1, 8));
        if (preg_match('/\bawait\s+(?:prisma|db|fetch|axios|http|supabase)|\.(?:findUnique|findMany|query)\s*\(/', $window)) {
            $findings[] = ['pillar' => 'Perf Profiler', 'severity' => 'HIGH', 'line' => $i + 2, 'msg' => 'N+1 DB/Network query inside loop — batch with WHERE IN / include / Promise.all'];
            $perfPen += 30;
        }
        if (preg_match('/(?:chat\.completions\.create|messages\.create|models\.generate_content|generateText)\s*\(/', $window)) {
            $findings[] = ['pillar' => 'Cloud FinOps', 'severity' => 'CRITICAL', 'line' => $i + 2, 'msg' => 'FINOPS-LLM-IN-LOOP: Paid LLM call inside loop ($50–$800 wallet-drain risk) — batch items!'];
            $perfPen += 35;
        }
    }
}

// 3. FinOps Infinite useEffect & Council TOCTOU / Missing Timeout Checks
if (preg_match('/useEffect\s*\(\s*\(\s*\)\s*=>\s*\{[\s\S]{1,360}?(?:onSnapshot|getDocs|fetch|axios|supabase)\b[\s\S]{1,200}?\}\s*\)/', $code, $m)) {
    if (!preg_match('/,\s*\[[^\]]*\]\s*\)\s*$/', trim($m[0]))) {
        $findings[] = ['pillar' => 'Cloud FinOps', 'severity' => 'CRITICAL', 'line' => 1, 'msg' => 'FINOPS-INF-USEEFFECT: Firestore/API read inside useEffect without [] array ($2,500/day loop)!'];
        $perfPen += 35;
    }
}
if (preg_match('/if\s*\(?\s*[\w.]*(?:balance|credits|wallet|stock)\s*>=?[\s\S]{1,200}?(?:balance|credits|wallet|stock)\s*-=/i', $code)) {
    $findings[] = ['pillar' => 'Council Exploit', 'severity' => 'CRITICAL', 'line' => 1, 'msg' => 'TOCTOU Double-Spend Race Condition on balance/wallet — use atomic SQL UPDATE WHERE balance >= ?'];
    $secPen += 35;
}
if (preg_match('/\b(?:requests|httpx)\.(?:get|post|put|delete)\s*\((?![^)]*\btimeout\s*=)[^)]+\)/', $code)) {
    $findings[] = ['pillar' => 'Council SRE', 'severity' => 'HIGH', 'line' => 1, 'msg' => 'Outbound HTTP call missing timeout= parameter — hung socket can freeze worker threads at 3 AM'];
    $perfPen += 20;
}

$secScore  = max(0, 100 - $secPen);
$perfScore = max(0, 100 - $perfPen);
$rtlScore  = max(0, 100 - $rtlPen);
$karpScore = max(0, 100 - $karpPen);
$overall   = (int)round(($secScore + $perfScore + $rtlScore + $karpScore) / 4);
$grade     = $overall >= 95 ? 'A+' : ($overall >= 85 ? 'A' : ($overall >= 70 ? 'B' : ($overall >= 55 ? 'C' : 'F')));

echo json_encode([
    'ok' => true,
    'version' => '12.0.0',
    'overall_score' => $overall,
    'grade' => $grade,
    'pillars' => [
        'security_sast' => $secScore,
        'perf_n_plus_1' => $perfScore,
        'rtl_ui_a11y'   => $rtlScore,
        'karpathy_sdk'  => $karpScore,
    ],
    'finding_count' => count($findings),
    'findings' => $findings,
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
