<?php
declare(strict_types=1);

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
$dbFile = $dataDir . '/leaderboard.sqlite';

try {
    $pdo = new PDO('sqlite:' . $dbFile);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS leaderboard (
            handle TEXT PRIMARY KEY,
            stack TEXT NOT NULL,
            tokens_saved INTEGER NOT NULL,
            usd_saved REAL NOT NULL,
            compression_pct REAL NOT NULL,
            grade TEXT NOT NULL,
            ip_hash TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ");

    $count = (int)$pdo->query("SELECT COUNT(*) FROM leaderboard")->fetchColumn();
    if ($count === 0) {
        $seed = [
            ['ElNeMeR', 'flutter', 18450000, 276.75, 96.8, 'A+'],
            ['alex-rustacean', 'rust', 12900000, 193.50, 95.4, 'A+'],
            ['sara-nextjs', 'nextjs', 9640000, 144.60, 94.9, 'A+'],
            ['kenji-go', 'go', 7820000, 117.30, 93.8, 'A'],
            ['omar-laravel', 'laravel', 6410000, 96.15, 96.1, 'A+'],
            ['lin-ai-infra', 'python', 5390000, 80.85, 95.2, 'A+'],
        ];
        $stmt = $pdo->prepare("
            INSERT OR IGNORE INTO leaderboard (handle, stack, tokens_saved, usd_saved, compression_pct, grade, ip_hash, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'seed', datetime('now'))
        ");
        foreach ($seed as $row) {
            $stmt->execute($row);
        }
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $raw = file_get_contents('php://input') ?: '';
        if (strlen($raw) > 4096) {
            http_response_code(413);
            echo json_encode(['ok' => false, 'error' => 'Payload too large']);
            exit;
        }
        $in = json_decode($raw, true);
        if (!is_array($in)) {
            http_response_code(400);
            echo json_encode(['ok' => false, 'error' => 'Invalid JSON']);
            exit;
        }

        $handle = preg_replace('/[^A-Za-z0-9_-]/', '', (string)($in['handle'] ?? 'anonymous-dev')) ?: 'anonymous-dev';
        $handle = substr($handle, 0, 28);
        $allowedStacks = ['flutter', 'nextjs', 'laravel', 'python', 'nodejs', 'rust', 'go', 'universal'];
        $stack = strtolower(trim((string)($in['stack'] ?? 'universal')));
        if (!in_array($stack, $allowedStacks, true)) {
            $stack = 'universal';
        }
        $tokens = max(100, min(500000000, (int)($in['tokens_saved'] ?? 25000)));
        $usd = round(max(0.01, min(7500.0, (float)($in['usd_saved'] ?? (($tokens / 1000000.0) * 15.0)))), 2);
        $pct = round(max(10.0, min(99.5, (float)($in['compression_pct'] ?? 95.0))), 1);
        $grade = preg_replace('/[^A-DF+-]/', '', strtoupper((string)($in['grade'] ?? 'A+'))) ?: 'A+';
        $grade = substr($grade, 0, 2);
        $ipHash = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0') . ':sqo_v8_salt'), 0, 16);

        $up = $pdo->prepare("
            INSERT INTO leaderboard (handle, stack, tokens_saved, usd_saved, compression_pct, grade, ip_hash, updated_at)
            VALUES (:h, :s, :t, :u, :p, :g, :ip, datetime('now'))
            ON CONFLICT(handle) DO UPDATE SET
                stack = excluded.stack,
                tokens_saved = MAX(leaderboard.tokens_saved, excluded.tokens_saved),
                usd_saved = MAX(leaderboard.usd_saved, excluded.usd_saved),
                compression_pct = excluded.compression_pct,
                grade = excluded.grade,
                updated_at = datetime('now')
        ");
        $up->execute([
            ':h' => $handle,
            ':s' => $stack,
            ':t' => $tokens,
            ':u' => $usd,
            ':p' => $pct,
            ':g' => $grade,
            ':ip' => $ipHash,
        ]);

        echo json_encode([
            'ok' => true,
            'handle' => $handle,
            'card_url' => 'https://sqo.elnemer-ai.com/api/card.php?handle=' . rawurlencode($handle),
        ], JSON_UNESCAPED_SLASHES);
        exit;
    }

    $totals = $pdo->query("
        SELECT
            COUNT(*) AS total_developers,
            COALESCE(SUM(tokens_saved), 0) AS total_tokens_saved,
            ROUND(COALESCE(SUM(usd_saved), 0), 2) AS total_usd_saved,
            ROUND(COALESCE(AVG(compression_pct), 95.5), 1) AS avg_compression_pct
        FROM leaderboard
    ")->fetch(PDO::FETCH_ASSOC);

    $leaders = $pdo->query("
        SELECT handle, stack, tokens_saved, usd_saved, compression_pct, grade, updated_at
        FROM leaderboard
        ORDER BY tokens_saved DESC
        LIMIT 15
    ")->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode([
        'ok' => true,
        'version' => '8.0.0',
        'network_totals' => [
            'total_developers' => (int)$totals['total_developers'],
            'total_tokens_saved' => (int)$totals['total_tokens_saved'],
            'total_usd_saved' => (float)$totals['total_usd_saved'],
            'avg_compression_pct' => (float)$totals['avg_compression_pct'],
        ],
        'leaderboard' => $leaders,
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Telemetry unavailable']);
}
