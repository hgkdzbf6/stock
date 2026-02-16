/** 缓存工具 */
interface CacheItem<T> {
  data: T;
  timestamp: number;
  expireTime: number;
}

class CacheService {
  private memoryCache: Map<string, CacheItem<any>> = new Map();
  
  /**
   * 获取缓存数据
   * @param key 缓存键
   * @param maxAge 最大缓存时间（毫秒），默认5分钟
   */
  get<T>(key: string, maxAge: number = 5 * 60 * 1000): T | null {
    // 先检查内存缓存
    const memoryItem = this.memoryCache.get(key);
    if (memoryItem) {
      const now = Date.now();
      if (now - memoryItem.timestamp < memoryItem.expireTime) {
        console.log(`[缓存命中] ${key} (内存缓存，剩余 ${Math.round((memoryItem.timestamp + memoryItem.expireTime - now) / 1000)}秒)`);
        return memoryItem.data;
      } else {
        console.log(`[缓存过期] ${key} (内存缓存)`);
        this.memoryCache.delete(key);
      }
    }
    
    // 检查localStorage缓存
    try {
      const localStorageItem = localStorage.getItem(`cache_${key}`);
      if (localStorageItem) {
        const parsed = JSON.parse(localStorageItem) as CacheItem<T>;
        const now = Date.now();
        
        if (now - parsed.timestamp < parsed.expireTime) {
          // 将localStorage的数据同步到内存缓存
          this.memoryCache.set(key, parsed);
          console.log(`[缓存命中] ${key} (localStorage缓存，剩余 ${Math.round((parsed.timestamp + parsed.expireTime - now) / 1000)}秒)`);
          return parsed.data;
        } else {
          console.log(`[缓存过期] ${key} (localStorage缓存)`);
          localStorage.removeItem(`cache_${key}`);
        }
      }
    } catch (error) {
      console.warn(`读取localStorage缓存失败: ${key}`, error);
    }
    
    return null;
  }
  
  /**
   * 设置缓存数据
   * @param key 缓存键
   * @param data 缓存数据
   * @param maxAge 最大缓存时间（毫秒），默认5分钟
   */
  set<T>(key: string, data: T, maxAge: number = 5 * 60 * 1000): void {
    const now = Date.now();
    const cacheItem: CacheItem<T> = {
      data,
      timestamp: now,
      expireTime: maxAge,
    };
    
    // 保存到内存缓存
    this.memoryCache.set(key, cacheItem);
    
    // 保存到localStorage缓存
    try {
      localStorage.setItem(`cache_${key}`, JSON.stringify(cacheItem));
      console.log(`[缓存已保存] ${key} (有效期 ${Math.round(maxAge / 1000)}秒)`);
    } catch (error) {
      console.warn(`保存localStorage缓存失败: ${key}`, error);
    }
  }
  
  /**
   * 删除指定缓存
   * @param key 缓存键
   */
  delete(key: string): void {
    this.memoryCache.delete(key);
    try {
      localStorage.removeItem(`cache_${key}`);
    } catch (error) {
      console.warn(`删除localStorage缓存失败: ${key}`, error);
    }
  }
  
  /**
   * 清除所有缓存
   */
  clear(): void {
    this.memoryCache.clear();
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('cache_')) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('清除localStorage缓存失败', error);
    }
  }
  
  /**
   * 清除过期缓存
   */
  clearExpired(): void {
    const now = Date.now();
    
    // 清除内存缓存中的过期数据
    for (const [key, item] of this.memoryCache.entries()) {
      if (now - item.timestamp >= item.expireTime) {
        this.memoryCache.delete(key);
      }
    }
    
    // 清除localStorage中的过期数据
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('cache_')) {
          const item = localStorage.getItem(key);
          if (item) {
            try {
              const parsed = JSON.parse(item) as CacheItem<any>;
              if (now - parsed.timestamp >= parsed.expireTime) {
                localStorage.removeItem(key);
              }
            } catch (error) {
              // 解析失败，直接删除
              localStorage.removeItem(key);
            }
          }
        }
      });
    } catch (error) {
      console.warn('清除过期缓存失败', error);
    }
  }
  
  /**
   * 获取缓存统计信息
   */
  getStats(): { memoryCount: number; localStorageCount: number } {
    let localStorageCount = 0;
    try {
      const keys = Object.keys(localStorage);
      localStorageCount = keys.filter(key => key.startsWith('cache_')).length;
    } catch (error) {
      console.warn('获取localStorage缓存统计失败', error);
    }
    
    return {
      memoryCount: this.memoryCache.size,
      localStorageCount,
    };
  }
}

// 创建全局缓存实例
export const cacheService = new CacheService();

// 页面加载时清除过期缓存
if (typeof window !== 'undefined') {
  cacheService.clearExpired();
}

export default cacheService;