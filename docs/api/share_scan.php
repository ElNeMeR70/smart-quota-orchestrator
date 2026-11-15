<?php
declare(strict_types=1);

/**
 * Smart Quota & Superpowers OS v12.0 Quantum — Shareable Diagnostic Permalink Registry
 * Endpoint: https://sqo.elnemer-ai.com/api/share_scan.php
 * - GET  ?id=abc12345  -> Fetches saved anonymized diagnostic scorecard
 * - POST {score, grade, summary, findings_text} -> Creates 8-char permalink ID in SQLite
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    @mkdir($dataDir, 0755, true);
}

try {
    $db = new PDO('sqlite:' . $dataDir . '/shared_scans.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec("
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            overall_score INTEGER NOT NULL,
            grade TEXT NOT NULL,
            report_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ");

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $raw = file_get_contents('php://input') ?: '';
        $in = json_decode($raw, true);
        if (!is_array($in)) {
            http_response_code(400);
            echo json_encode(['ok' => false, 'error' => 'Invalid JSON']);
            exit;
        }
        $score = max(0, min(100, (int)($in['overall_score'] ?? 100)));
        $grade = preg_replace('/[^A-F+]/', '', (string)($in['grade'] ?? 'A+')) ?: 'A';
        $report = substr(trim((string)($in['report_text'] ?? '')), 0, 4000);
        // Scrub any accidental keys before saving
        $report = preg_replace('/\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b/', '<REDACTED>', $report);

        $id = substr(bin2hex(random_bytes(5)), 0, 8);
        $stmt = $db->prepare("INSERT INTO scans(scan_id, overall_score, grade, report_text, created_at) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([$id, $score, $grade, $report, gmdate('Y-m-d\TH:i:s\Z')]);

        echo json_encode([
            'ok' => true,
            'scan_id' => $id,
            'share_url' => 'https://sqo.elnemer-ai.com/?scan=' . $id . '#apex-radar',
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $id = preg_replace('/[^a-f0-9]/', '', strtolower((string)($_GET['id'] ?? '')));
    $stmt = $db->prepare("SELECT scan_id, overall_score, grade, report_text, created_at FROM scans WHERE scan_id = ?");
    $stmt->execute([$id]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$row) {
        http_response_code(404);
        echo json_encode(['ok' => false, 'error' => 'Scan permalink not found']);
        exit;
    }
    echo json_encode(['ok' => true, 'scan' => $row], JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Storage unavailable']);
}
