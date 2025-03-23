// 飞书API配置
const FEISHU_CONFIG = {
  APP_ID: "cli_a75472bbb83a500d",
  APP_SECRET: "YoCfSgSr6pHgeRQqV6skJcuwwhOlmf4n",
  BASE_ID: "D0olbfeHEaDMPqsz3f2c17adnyd",
  TABLE_ID: "tblBzpqhO3ODWOE7"
};

// 飞书API基础URL
const FEISHU_BASE_URL = "https://open.feishu.cn/open-apis/";

// 监听来自popup的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  // 确保响应函数不会过早返回
  let handled = false;
  
  if (request.action === 'saveLink') {
    // 处理保存链接请求
    handleSaveLinkRequest(request.data)
      .then(result => {
        sendResponse({success: true});
      })
      .catch(error => {
        console.error('Error saving link:', error);
        sendResponse({success: false, error: error.message});
      })
      .finally(() => {
        handled = true;
      });
  }
  
  // 返回true表示将异步发送响应
  return true;
});

/**
 * 处理保存链接请求
 * @param {Object} data - 包含url和title的对象
 * @returns {Promise} - 处理结果的Promise
 */
async function handleSaveLinkRequest(data) {
  try {
    // 1. 获取飞书访问令牌
    const token = await getFeishuToken();
    if (!token) {
      throw new Error('无法获取飞书访问令牌');
    }
    
    // 2. 将链接保存到多维表格
    await saveLinkToFeishuTable(token, data);
    
    return {success: true};
  } catch (error) {
    console.error('Error in handleSaveLinkRequest:', error);
    throw error;
  }
}

/**
 * 获取飞书访问令牌
 * @returns {Promise<string>} - 飞书访问令牌
 */
async function getFeishuToken() {
  try {
    const url = `${FEISHU_BASE_URL}auth/v3/tenant_access_token/internal`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        app_id: FEISHU_CONFIG.APP_ID,
        app_secret: FEISHU_CONFIG.APP_SECRET
      })
    });
    
    if (!response.ok) {
      throw new Error(`获取令牌请求失败，状态码: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.code === 0) {
      return result.tenant_access_token;
    } else {
      throw new Error(`获取令牌失败，错误码: ${result.code}，错误信息: ${result.msg}`);
    }
  } catch (error) {
    console.error('Error getting Feishu token:', error);
    throw new Error(`获取飞书访问令牌失败: ${error.message}`);
  }
}

/**
 * 将链接保存到飞书多维表格
 * @param {string} token - 飞书访问令牌
 * @param {Object} data - 包含url和title的对象
 * @returns {Promise} - 保存结果的Promise
 */
async function saveLinkToFeishuTable(token, data) {
  try {
    const url = `${FEISHU_BASE_URL}bitable/v1/apps/${FEISHU_CONFIG.BASE_ID}/tables/${FEISHU_CONFIG.TABLE_ID}/records`;
    
    // 构建记录数据
    // 注意：这里的字段名称需要与多维表格中的字段名称匹配
    const recordData = {
      fields: {
        "链接": {
          "text": data.title,
          "link": data.url
        }
      }
    };
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(recordData)
    });
    
    if (!response.ok) {
      throw new Error(`保存链接请求失败，状态码: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.code === 0) {
      return result.data;
    } else {
      throw new Error(`保存链接失败，错误码: ${result.code}，错误信息: ${result.msg}`);
    }
  } catch (error) {
    console.error('Error saving link to Feishu table:', error);
    throw new Error(`保存链接到飞书多维表格失败: ${error.message}`);
  }
}