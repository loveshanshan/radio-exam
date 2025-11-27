const fs = require('fs');
const path = require('path');

// 检查Vue文件语法
function checkVueFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        console.log(`✓ ${filePath} - 文件读取成功`);
        
        // 简单的语法检查
        const scriptMatch = content.match(/<script setup>([\s\S]*?)<\/script>/);
        if (scriptMatch) {
            const scriptContent = scriptMatch[1];
            
            // 检查重复声明
            const constDeclarations = scriptContent.match(/const\s+(\w+)\s*=/g);
            if (constDeclarations) {
                const variables = {};
                constDeclarations.forEach(decl => {
                    const match = decl.match(/const\s+(\w+)\s*=/);
                    if (match) {
                        const varName = match[1];
                        if (variables[varName]) {
                            console.log(`❌ ${filePath} - 重复声明: ${varName}`);
                            return false;
                        }
                        variables[varName] = true;
                    }
                });
                console.log(`✓ ${filePath} - 无重复声明`);
            }
        }
        
        return true;
    } catch (error) {
        console.log(`❌ ${filePath} - 错误: ${error.message}`);
        return false;
    }
}

// 检查所有Vue组件
const componentsDir = path.join(__dirname, 'frontend/src/components');
const files = fs.readdirSync(componentsDir);

console.log('检查Vue组件语法...\n');

let allValid = true;
files.forEach(file => {
    if (file.endsWith('.vue')) {
        const filePath = path.join(componentsDir, file);
        const isValid = checkVueFile(filePath);
        allValid = allValid && isValid;
    }
});

if (allValid) {
    console.log('\n✅ 所有Vue组件语法检查通过！');
} else {
    console.log('\n❌ 发现语法错误，请修复后重试！');
    process.exit(1);
}