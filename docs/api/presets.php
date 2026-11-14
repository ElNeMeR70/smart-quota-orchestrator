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
$dbFile = $dataDir . '/presets_hub.sqlite';

try {
    $pdo = new PDO('sqlite:' . $dbFile);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stack TEXT NOT NULL,
            title TEXT NOT NULL,
            rule TEXT NOT NULL,
            author TEXT NOT NULL,
            downloads INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ");

    $count = (int)$pdo->query("SELECT COUNT(*) FROM presets")->fetchColumn();
    if ($count === 0) {
        $seed = [
            ['flutter', 'Flutter Clean Arch & Codegen Shield', 'Never read *.g.dart, *.freezed.dart, pubspec.lock, or .dart_tool/. Audit localization drift via sqo_i18n_audit instead of dumping .arb files.', 'ElNeMeR', 412],
            ['nextjs', 'Next.js 15 App Router Zero-Waste Protocol', 'Map endpoints via sqo_api_routes first; block .next/ & package-lock.json; extract backend DTO contracts via sqo_api_contracts.', 'ElNeMeR', 389],
            ['laravel', 'Laravel 11 SaaS Migration & Schema Distiller', 'Never read 50+ database/migrations/*.php files raw; run sqo_schema_distill for a <300-token ER DSL and ignore _ide_helper.php.', 'ElNeMeR', 341],
            ['python', 'FastAPI / AI Agent Zero-Hallucination Guard', 'Verify imports against pyproject.toml with sqo_verify_deps and run <12ms AST pre-flight sqo_shadow_check before pytest.', 'ElNeMeR', 298],
            ['rust', 'Rust Cargo & Borrow-Checker Fast Loop', 'Ignore target/ and Cargo.lock; run sqo_shadow_check to verify delimiter balance before triggering expensive cargo check builds.', 'alex-rustacean', 215],
            ['go', 'Go Microservices Blast-Radius Isolation', 'Use sqo_blast_radius to run go test ONLY on affected packages instead of full-repo test sweeps.', 'kenji-go', 184],
            ['universal', '90% LLM KV-Cache Prefix Protection', 'Never inject timestamps, random UUIDs, or unsorted file walks into system rules; verify 100/100 score with sqo_cache_audit.', 'ElNeMeR', 520],
            ['universal', 'Surgical Time-Machine Checkpoints Before Swarms', 'Create a zlib snapshot via sqo_checkpoint before launching multi-file refactors so rollbacks take 20ms with zero git reset risk.', 'ElNeMeR', 467],
        ];
        $ins = $pdo->prepare("INSERT INTO presets (stack, title, rule, author, downloads, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))");
        foreach ($seed as $r) {
            $ins->execute($r);
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
        $allowed = ['flutter', 'nextjs', 'laravel', 'python', 'nodejs', 'rust', 'go', 'universal'];
        $stack = strtolower(trim((string)($in['stack'] ?? 'universal')));
        if (!in_array($stack, $allowed, true)) $stack = 'universal';

        $title = trim(strip_tags((string)($in['title'] ?? '')));
        $rule = trim(strip_tags((string)($in['rule'] ?? '')));
        $author = preg_replace('/[^A-Za-z0-9_-]/', '', (string)($in['author'] ?? 'community-dev')) ?: 'community-dev';

        if (strlen($title) < 5 || strlen($rule) < 15) {
            http_response_code(422);
            echo json_encode(['ok' => false, 'error' => 'Title or rule too short']);
            exit;
        }
        if (preg_match('/(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,})/', $rule)) {
            http_response_code(422);
            echo json_encode(['ok' => false, 'error' => 'Secret token pattern rejected by DLP guard']);
            exit;
        }

        $stmt = $pdo->prepare("INSERT INTO presets (stack, title, rule, author, downloads, created_at) VALUES (?, ?, ?, ?, 1, datetime('now'))");
        $stmt->execute([substr($stack, 0, 24), substr($title, 0, 90), substr($rule, 0, 420), substr($author, 0, 28)]);
        echo json_encode(['ok' => true, 'id' => (int)$pdo->lastInsertId()]);
        exit;
    }

    $stackFilter = strtolower(trim((string)($_GET['stack'] ?? '')));
    if ($stackFilter !== '' && $stackFilter !== 'all') {
        $stmt = $pdo->prepare("SELECT id, stack, title, rule, author, downloads, created_at FROM presets WHERE stack IN (?, 'universal') ORDER BY downloads DESC, id DESC LIMIT 30");
        $stmt->execute([$stackFilter]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } else {
        $rows = $pdo->query("SELECT id, stack, title, rule, author, downloads, created_at FROM presets ORDER BY downloads DESC, id DESC LIMIT 30")->fetchAll(PDO::FETCH_ASSOC);
    }

    echo json_encode([
        'ok' => true,
        'version' => '9.0.0',
        'count' => count($rows),
        'presets' => $rows,
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Hub unavailable']);
}
