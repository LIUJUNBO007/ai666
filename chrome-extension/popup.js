// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  // 获取DOM元素
  const saveButton = document.getElementById('saveLink');
  const statusMessage = document.getElementById('statusMessage');
  
  // 为保存按钮添加点击事件监听器
  saveButton.addEventListener('click', async function() {
    try {
      // 更新UI状态为加载中
      setLoading(true);
      setStatus('正在处理...', 'loading');
      
      // 获取当前标签页信息
      const tabs = await chrome.tabs.query({active: true, currentWindow: true});
      const currentTab = tabs[0];
      
      // 提取URL和域名
      const url = currentTab.url;
      const domain = extractDomain(url);
      
      // 发送消息给后台服务
      chrome.runtime.sendMessage({
        action: 'saveLink',
        data: {
          url: url,
          title: domain
        }
      }, function(response) {
        // 处理响应
        if (response.success) {
          setStatus('链接保存成功！', 'success');
        } else {
          setStatus(`保存失败: ${response.error}`, 'error');
        }
        setLoading(false);
      });
    } catch (error) {
      console.error('Error:', error);
      setStatus(`发生错误: ${error.message}`, 'error');
      setLoading(false);
    }
  });
  
  // 辅助函数：从URL中提取域名
  function extractDomain(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch (e) {
      console.error('Invalid URL:', url);
      return url; // 如果URL无效，返回原始URL
    }
  }
  
  // 辅助函数：设置加载状态
  function setLoading(isLoading) {
    saveButton.disabled = isLoading;
    
    // 如果正在加载，添加加载动画
    if (isLoading) {
      statusMessage.innerHTML = '<span class="spinner"></span>' + statusMessage.innerHTML;
    } else {
      // 移除加载动画
      const spinner = statusMessage.querySelector('.spinner');
      if (spinner) {
        spinner.remove();
      }
    }
  }
  
  // 辅助函数：设置状态消息
  function setStatus(message, type) {
    statusMessage.textContent = message;
    
    // 移除所有状态类
    statusMessage.classList.remove('success', 'error', 'loading');
    
    // 添加对应的状态类
    if (type) {
      statusMessage.classList.add(type);
    }
  }
});