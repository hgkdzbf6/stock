#!/bin/bash
# 行情页面修复执行脚本

echo "=================================="
echo "  行情页面修复"
echo "=================================="
echo ""

# 停止服务
echo "1. 停止服务..."
./stop_all.sh
echo ""

# 备份文件
echo "2. 备份文件..."
mkdir -p .backup_$(date +%Y%m%d_%H%M%S)
cp backend/services/data_download_service.py .backup_$(date +%Y%m%d_%H%M%S)/
cp backend/services/duckdb_storage_service.py .backup_$(date +%Y%m%d_%H%M%S)/
cp backend/api/__init__.py .backup_$(date +%Y%m%d_%H%M%S)/
cp frontend/src/pages/Market.tsx .backup_$(date +%Y%m%d_%H%M%S)/
echo "✅ 文件已备份"
echo ""

# 应用修复
echo "3. 应用修复..."

# 应用data_download_service修复
echo "   - 应用data_download_service修复..."
cp backend/services/data_download_service_fixed.py backend/services/data_download_service.py
echo "   ✅ 完成"

# 应用duckdb_storage_service修复
echo "   - 应用duckdb_storage_service修复..."
cp backend/services/duckdb_storage_service_fixed.py backend/services/duckdb_storage_service.py
echo "   ✅ 完成"

# 检查并添加板块路由
echo "   - 检查板块路由..."
if grep -q "from api.sector import router as sector_router" backend/api/__init__.py; then
    echo "   ⚠️  板块路由已存在，跳过"
else
    echo "   - 添加板块路由..."
    # 在api_router定义之后添加板块路由
    sed -i '' '/api_router = APIRouter(prefix="\/api\/v1")/a\
\
from api.sector import router as sector_router\
\
# 注册板块路由\
api_router.include_router(sector_router, prefix="/api/v1")
' backend/api/__init__.py
    echo "   ✅ 完成"
fi
echo ""

# 修改Market页面
echo "4. 修改Market页面..."
# 添加sectorService导入
if ! grep -q "import { sectorService } from '@services/sector'" frontend/src/pages/Market.tsx; then
    sed -i '' "/import { stockService } from '@services\/stock';/a\\
import { sectorService } from '@services/sector';
" frontend/src/pages/Market.tsx
    echo "   ✅ 添加sectorService导入"
fi

# 添加板块列表状态
if ! grep -q "const \[sectors, setSectors\]" frontend/src/pages/Market.tsx; then
    sed -i '' "/const \[filters, setFilters\]/a\\
  const \[sectors, setSectors\] = useState<any\[\]>([]);
" frontend/src/pages/Market.tsx
    echo "   ✅ 添加板块状态"
fi

# 添加加载板块列表的useEffect
if ! grep -q "sectorService.getSectorList" frontend/src/pages/Market.tsx; then
    sed -i '' '/\/\/ 初始加载/a\
  // 加载板块列表\
  useEffect(() => {\
    sectorService.getSectorList()\
      .then(setSectors)\
      .catch(error => {\
        console.error('"'"'获取板块列表失败:'"'"', error);\
      });\
  }, []);
' frontend/src/pages/Market.tsx
    echo "   ✅ 添加板块加载逻辑"
fi

# 替换硬编码的板块选项
if grep -q '<Option value="医药">医药</Option>' frontend/src/pages/Market.tsx; then
    sed -i '' '/<Option value="医药">医药<\/Option>/,/^[[:space:]]*<\/Select>/c\
        {/* ✅ 使用动态板块列表 */}\
        {sectors.map(sector => (\
          <Option key={sector.code} value={sector.code}>\
            {sector.name}\
          </Option>\
        ))}
      </Select>' frontend/src/pages/Market.tsx
    echo "   ✅ 替换为动态板块列表"
fi
echo ""

# 清理备份文件
echo "5. 清理修复文件..."
rm -f backend/services/data_download_service_fixed.py
rm -f backend/services/duckdb_storage_service_fixed.py
echo "   ✅ 完成"
echo ""

# 启动服务
echo "6. 启动服务..."
./start_all.sh
echo ""

echo "=================================="
echo "  ✅ 修复完成！"
echo "=================================="
echo ""
echo "📝 修复内容："
echo "   ✅ 行情页面使用本地数据（而非CSV）"
echo "   ✅ 股票名称从本地获取（不再显示'未知'）"
echo "   ✅ 板块列表动态加载"
echo "   ✅ 板块API已注册"
echo ""
echo "🌐 访问地址："
echo "   前端应用:   http://localhost:3000/market"
echo "   后端API:    http://localhost:8000/docs"
echo "   健康检查:   http://localhost:8000/health"
echo ""
echo "📊 测试步骤："
echo "   1. 访问 http://localhost:3000/data-download 下载数据"
echo "   2. 访问 http://localhost:3000/market 查看行情"
echo "   3. 验证股票名称正确显示（非'未知'）"
echo "   4. 验证板块列表正确加载"
echo "   5. 验证显示的是已下载的数据"
echo ""