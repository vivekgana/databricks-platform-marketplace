#!/usr/bin/env node

/**
 * Validation script for Databricks Platform Marketplace
 * Validates all plugin configurations and marketplace manifest
 */

const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m'
};

let errors = [];
let warnings = [];

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function validateJSON(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const parsed = JSON.parse(content);
        log(`  ✓ ${path.basename(filePath)} is valid JSON`, colors.green);
        return parsed;
    } catch (error) {
        errors.push(`${filePath}: Invalid JSON - ${error.message}`);
        log(`  ✗ ${path.basename(filePath)} is invalid JSON`, colors.red);
        return null;
    }
}

function validateMarketplaceManifest() {
    log('\n📦 Validating marketplace manifest...', colors.cyan);
    
    const manifestPath = '.claude-plugin/marketplace.json';
    const manifest = validateJSON(manifestPath);
    
    if (!manifest) return;
    
    // Required fields
    const required = ['name', 'version', 'owner', 'metadata', 'plugins'];
    for (const field of required) {
        if (!manifest[field]) {
            errors.push(`marketplace.json: Missing required field '${field}'`);
        }
    }
    
    // Validate owner
    if (manifest.owner) {
        if (!manifest.owner.name || !manifest.owner.url) {
            errors.push('marketplace.json: Owner must have name and url');
        }
    }
    
    // Validate plugins array
    if (manifest.plugins && Array.isArray(manifest.plugins)) {
        log(`  Found ${manifest.plugins.length} plugins`, colors.green);
        
        for (const plugin of manifest.plugins) {
            if (!plugin.name || !plugin.path) {
                errors.push('marketplace.json: Each plugin must have name and path');
            }
        }
    }
    
    log('  ✓ Marketplace manifest structure valid', colors.green);
}

function validatePluginConfig(pluginPath) {
    const pluginName = path.basename(pluginPath);
    log(`\n🔌 Validating plugin: ${pluginName}...`, colors.cyan);
    
    const configPath = path.join(pluginPath, '.claude-plugin/plugin.json');
    
    if (!fs.existsSync(configPath)) {
        errors.push(`${pluginName}: plugin.json not found`);
        return;
    }
    
    const config = validateJSON(configPath);
    if (!config) return;
    
    // Required fields
    const required = ['name', 'version', 'description'];
    for (const field of required) {
        if (!config[field]) {
            errors.push(`${pluginName}/plugin.json: Missing required field '${field}'`);
        }
    }
    
    // Validate commands
    if (config.commands) {
        log(`  Found ${config.commands.length} commands`, colors.green);
        
        for (const cmd of config.commands) {
            const cmdPath = path.join(pluginPath, cmd.path);
            if (!fs.existsSync(cmdPath)) {
                warnings.push(`${pluginName}: Command file not found: ${cmd.path}`);
            }
        }
    }
    
    // Validate agents
    if (config.agents) {
        log(`  Found ${config.agents.length} agents`, colors.green);
        
        for (const agent of config.agents) {
            const agentPath = path.join(pluginPath, agent.path);
            if (!fs.existsSync(agentPath)) {
                warnings.push(`${pluginName}: Agent file not found: ${agent.path}`);
            }
        }
    }
    
    // Validate skills
    if (config.skills) {
        log(`  Found ${config.skills.length} skills`, colors.green);
        
        for (const skill of config.skills) {
            const skillPath = path.join(pluginPath, skill.path);
            if (!fs.existsSync(skillPath)) {
                warnings.push(`${pluginName}: Skill directory not found: ${skill.path}`);
            } else {
                // Check for SKILL.md
                const skillMd = path.join(skillPath, 'SKILL.md');
                if (!fs.existsSync(skillMd)) {
                    warnings.push(`${pluginName}: SKILL.md not found in ${skill.path}`);
                }
            }
        }
    }
    
    log(`  ✓ Plugin ${pluginName} configuration valid`, colors.green);
}

function validatePlugins() {
    const pluginsDir = 'plugins';
    
    if (!fs.existsSync(pluginsDir)) {
        errors.push('plugins/ directory not found');
        return;
    }
    
    const plugins = fs.readdirSync(pluginsDir, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name);
    
    for (const plugin of plugins) {
        validatePluginConfig(path.join(pluginsDir, plugin));
    }
}

function validatePackageJson() {
    log('\n📄 Validating package.json...', colors.cyan);
    
    const pkg = validateJSON('package.json');
    if (!pkg) return;
    
    if (!pkg['claude-plugin']) {
        warnings.push('package.json: Missing claude-plugin configuration');
    }
    
    if (pkg['claude-plugin'] && !pkg['claude-plugin'].marketplace) {
        warnings.push('package.json: claude-plugin.marketplace should be true');
    }
    
    log('  ✓ package.json valid', colors.green);
}

function validateFileStructure() {
    log('\n📁 Validating file structure...', colors.cyan);
    
    const requiredFiles = [
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'package.json',
        '.claude-plugin/marketplace.json',
        '.gitignore',
        'requirements.txt'
    ];
    
    for (const file of requiredFiles) {
        if (!fs.existsSync(file)) {
            errors.push(`Required file missing: ${file}`);
        } else {
            log(`  ✓ ${file} exists`, colors.green);
        }
    }
}

function printSummary() {
    log('\n' + '='.repeat(60), colors.cyan);
    log('VALIDATION SUMMARY', colors.cyan);
    log('='.repeat(60), colors.cyan);
    
    if (errors.length === 0 && warnings.length === 0) {
        log('\n✅ All validations passed!', colors.green);
        log('🎉 Marketplace is ready for publication!', colors.green);
        return 0;
    }
    
    if (errors.length > 0) {
        log(`\n❌ ${errors.length} Error(s) found:`, colors.red);
        errors.forEach(error => log(`  • ${error}`, colors.red));
    }
    
    if (warnings.length > 0) {
        log(`\n⚠️  ${warnings.length} Warning(s):`, colors.yellow);
        warnings.forEach(warning => log(`  • ${warning}`, colors.yellow));
    }
    
    if (errors.length > 0) {
        log('\n❌ Validation failed. Please fix errors above.', colors.red);
        return 1;
    } else {
        log('\n⚠️  Validation passed with warnings. Consider fixing them.', colors.yellow);
        return 0;
    }
}

// Main execution
function main() {
    log('🔍 Starting validation...', colors.cyan);
    
    validateMarketplaceManifest();
    validatePackageJson();
    validatePlugins();
    validateFileStructure();
    
    const exitCode = printSummary();
    process.exit(exitCode);
}

main();
