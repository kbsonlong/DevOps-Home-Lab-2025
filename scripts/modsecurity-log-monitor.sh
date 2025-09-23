#!/bin/bash

# ModSecurity 日志监控脚本
# 用于实时监控和分析 ModSecurity 日志

set -e

# 配置变量
LOG_DIR="/var/log/modsecurity"
AUDIT_LOG="$LOG_DIR/modsec_audit.log"
DEBUG_LOG="$LOG_DIR/modsec_debug.log"
ALERT_THRESHOLD=10  # 10秒内超过此数量的警告将触发告警

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查日志文件是否存在
check_log_files() {
    log_info "检查 ModSecurity 日志文件..."
    
    if [ ! -f "$AUDIT_LOG" ]; then
        log_warn "审计日志文件不存在: $AUDIT_LOG"
        return 1
    fi
    
    if [ ! -f "$DEBUG_LOG" ]; then
        log_warn "调试日志文件不存在: $DEBUG_LOG"
        return 1
    fi
    
    log_success "日志文件检查完成"
    return 0
}

# 分析审计日志
analyze_audit_log() {
    log_info "分析审计日志..."
    
    if [ ! -f "$AUDIT_LOG" ]; then
        log_warn "审计日志文件不存在"
        return 1
    fi
    
    # 统计过去1小时的攻击类型
    local current_time=$(date +%s)
    local one_hour_ago=$((current_time - 3600))
    
    echo -e "\n${BLUE}=== 审计日志分析 ===${NC}"
    echo -e "${YELLOW}时间范围: 过去1小时${NC}"
    
    # SQL注入攻击统计
    local sql_injection_count=$(grep -c "SQL Injection Attack" "$AUDIT_LOG" 2>/dev/null || echo "0")
    echo -e "${RED}SQL注入攻击: $sql_injection_count${NC}"
    
    # XSS攻击统计
    local xss_count=$(grep -c "XSS Attack" "$AUDIT_LOG" 2>/dev/null || echo "0")
    echo -e "${RED}XSS攻击: $xss_count${NC}"
    
    # 目录遍历攻击统计
    local traversal_count=$(grep -c "Directory Traversal" "$AUDIT_LOG" 2>/dev/null || echo "0")
    echo -e "${RED}目录遍历攻击: $traversal_count${NC}"
    
    # 总攻击次数
    local total_attacks=$((sql_injection_count + xss_count + traversal_count))
    echo -e "${YELLOW}总攻击次数: $total_attacks${NC}"
    
    # 显示最新的攻击详情
    if [ $total_attacks -gt 0 ]; then
        echo -e "\n${BLUE}=== 最新攻击详情 ===${NC}"
        tail -n 20 "$AUDIT_LOG" | grep -E "(SQL Injection|XSS Attack|Directory Traversal)" | tail -n 5
    fi
}

# 分析调试日志
analyze_debug_log() {
    log_info "分析调试日志..."
    
    if [ ! -f "$DEBUG_LOG" ]; then
        log_warn "调试日志文件不存在"
        return 1
    fi
    
    echo -e "\n${BLUE}=== 调试日志分析 ===${NC}"
    
    # 统计错误级别
    local error_count=$(grep -c "ERROR" "$DEBUG_LOG" 2>/dev/null || echo "0")
    local warn_count=$(grep -c "WARNING" "$DEBUG_LOG" 2>/dev/null || echo "0")
    local info_count=$(grep -c "INFO" "$DEBUG_LOG" 2>/dev/null || echo "0")
    
    echo -e "${RED}错误数量: $error_count${NC}"
    echo -e "${YELLOW}警告数量: $warn_count${NC}"
    echo -e "${GREEN}信息数量: $info_count${NC}"
    
    # 显示最新的错误
    if [ $error_count -gt 0 ]; then
        echo -e "\n${RED}=== 最新错误 ===${NC}"
        grep "ERROR" "$DEBUG_LOG" | tail -n 5
    fi
}

# 实时监控函数
monitor_logs() {
    log_info "开始实时监控 ModSecurity 日志..."
    log_info "按 Ctrl+C 停止监控"
    
    # 使用 tail 实时监控两个日志文件
    tail -f "$AUDIT_LOG" "$DEBUG_LOG" 2>/dev/null | while read -r line; do
        if echo "$line" | grep -q "ERROR"; then
            echo -e "${RED}[ERROR]${NC} $line"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "${YELLOW}[WARNING]${NC} $line"
        elif echo "$line" | grep -q "SQL Injection\|XSS Attack\|Directory Traversal"; then
            echo -e "${RED}[ATTACK]${NC} $line"
        else
            echo -e "${GREEN}[INFO]${NC} $line"
        fi
    done
}

# 生成报告
generate_report() {
    log_info "生成 ModSecurity 安全报告..."
    
    local report_file="/tmp/modsecurity_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ModSecurity 安全报告"
        echo "生成时间: $(date)"
        echo "================================"
        echo
        
        analyze_audit_log
        analyze_debug_log
        
        echo
        echo "================================"
        echo "报告生成完成: $report_file"
    } > "$report_file"
    
    log_success "报告已生成: $report_file"
    cat "$report_file"
}

# 清理旧日志
cleanup_logs() {
    log_info "清理超过30天的旧日志..."
    
    find "$LOG_DIR" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    find "$LOG_DIR" -name "*.log.*" -type f -mtime +30 -delete 2>/dev/null || true
    
    log_success "日志清理完成"
}

# 主函数
main() {
    echo -e "${BLUE}ModSecurity 日志监控工具${NC}"
    echo -e "${BLUE}========================${NC}"
    
    case "${1:-monitor}" in
        "check")
            check_log_files
            ;;
        "analyze")
            analyze_audit_log
            analyze_debug_log
            ;;
        "monitor")
            check_log_files && monitor_logs
            ;;
        "report")
            generate_report
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [命令]"
            echo "命令:"
            echo "  check    - 检查日志文件状态"
            echo "  analyze  - 分析日志内容"
            echo "  monitor  - 实时监控日志（默认）"
            echo "  report   - 生成安全报告"
            echo "  cleanup  - 清理旧日志"
            echo "  help     - 显示帮助信息"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看可用命令"
            exit 1
            ;;
    esac
}

# 如果直接运行脚本
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi