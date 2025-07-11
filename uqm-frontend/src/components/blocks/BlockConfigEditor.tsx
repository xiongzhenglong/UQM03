import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, Button, message, Space, Tabs } from 'antd';
import { CodeOutlined, SettingOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

interface BlockConfigEditorProps {
  visible: boolean;
  onCancel: () => void;
  onSave: (config: BlockConfig) => void;
  initialConfig?: BlockConfig;
  blockType: 'table' | 'chart';
}

export interface BlockConfig {
  title: string;
  description: string;
  uqmConfig: any;
  chartType?: 'bar' | 'line' | 'pie' | 'scatter';
}

// 预设的UQM查询模板
const UQM_TEMPLATES = {
  it_employees: {
    name: "IT部门员工查询",
    description: "查询信息技术部所有在职状态员工的详细信息",
    config: {
      "uqm": {
        "metadata": {
          "name": "get_it_department_active_employees",
          "description": "查询并返回信息技术部所有在职状态员工的详细信息。"
        },
        "steps": [
          {
            "name": "filter_it_department_employees",
            "type": "query",
            "config": {
              "data_source": "employees e",
              "dimensions": [
                {
                  "expression": "e.employee_id",
                  "alias": "employee_id"
                },
                {
                  "expression": "e.first_name",
                  "alias": "first_name"
                },
                {
                  "expression": "e.last_name",
                  "alias": "last_name"
                },
                {
                  "expression": "e.email",
                  "alias": "email"
                },
                {
                  "expression": "e.phone_number",
                  "alias": "phone_number"
                },
                {
                  "expression": "e.hire_date",
                  "alias": "hire_date"
                },
                {
                  "expression": "e.job_title",
                  "alias": "job_title"
                },
                {
                  "expression": "e.salary",
                  "alias": "salary"
                },
                {
                  "expression": "d.name",
                  "alias": "department_name"
                }
              ],
              "joins": [
                {
                  "type": "inner",
                  "target": "departments d",
                  "on": {
                    "left": "e.department_id",
                    "right": "d.department_id"
                  }
                }
              ],
              "filters": [
                {
                  "logic": "AND",
                  "conditions": [
                    {
                      "field": "d.name",
                      "operator": "=",
                      "value": "信息技术部"
                    },
                    {
                      "field": "e.is_active",
                      "operator": "=",
                      "value": true
                    }
                  ]
                }
              ]
            }
          }
        ],
        "output": "filter_it_department_employees"
      },
      "parameters": {},
      "options": {
        "dialect": "mysql",
        "page": 1,
        "page_size": 10
      }
    }
  },
  department_stats: {
    name: "部门统计",
    description: "统计各部门员工数量和平均薪资",
    config: {
      "uqm": {
        "metadata": {
          "name": "department_statistics",
          "description": "统计各部门员工数量和平均薪资"
        },
        "steps": [
          {
            "name": "department_stats",
            "type": "query",
            "config": {
              "data_source": "employees e",
              "dimensions": [
                {
                  "expression": "d.name",
                  "alias": "department_name"
                },
                {
                  "expression": "COUNT(*)",
                  "alias": "employee_count"
                },
                {
                  "expression": "AVG(e.salary)",
                  "alias": "avg_salary"
                }
              ],
              "joins": [
                {
                  "type": "inner",
                  "target": "departments d",
                  "on": {
                    "left": "e.department_id",
                    "right": "d.department_id"
                  }
                }
              ],
              "group_by": ["d.name"],
              "order_by": [
                {
                  "field": "employee_count",
                  "direction": "desc"
                }
              ]
            }
          }
        ],
        "output": "department_stats"
      },
      "parameters": {},
      "options": {
        "dialect": "mysql"
      }
    }
  }
};

const BlockConfigEditor: React.FC<BlockConfigEditorProps> = ({
  visible,
  onCancel,
  onSave,
  initialConfig,
  blockType
}) => {
  const [form] = Form.useForm();
  const [uqmJson, setUqmJson] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);

  useEffect(() => {
    if (visible && initialConfig) {
      form.setFieldsValue({
        title: initialConfig.title,
        description: initialConfig.description,
        chartType: initialConfig.chartType || 'bar'
      });
      setUqmJson(JSON.stringify(initialConfig.uqmConfig, null, 2));
    } else if (visible) {
      form.resetFields();
      setUqmJson('');
    }
  }, [visible, initialConfig, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 验证JSON格式
      let parsedUqmConfig;
      try {
        parsedUqmConfig = JSON.parse(uqmJson);
        setJsonError(null);
      } catch (error) {
        setJsonError('UQM配置JSON格式错误');
        return;
      }

      const config: BlockConfig = {
        title: values.title,
        description: values.description,
        uqmConfig: parsedUqmConfig,
        ...(blockType === 'chart' && { chartType: values.chartType })
      };

      onSave(config);
      message.success('配置保存成功');
    } catch (error) {
      console.error('保存配置失败:', error);
    }
  };

  const handleTemplateSelect = (templateKey: string) => {
    const template = UQM_TEMPLATES[templateKey as keyof typeof UQM_TEMPLATES];
    if (template) {
      form.setFieldsValue({
        title: template.name,
        description: template.description
      });
      setUqmJson(JSON.stringify(template.config, null, 2));
      setJsonError(null);
    }
  };

  const validateJson = (value: string) => {
    try {
      JSON.parse(value);
      setJsonError(null);
    } catch (error) {
      setJsonError('JSON格式错误');
    }
  };

  return (
    <Modal
      title="区块配置"
      open={visible}
      onCancel={onCancel}
      onOk={handleSave}
      width={800}
      okText="保存"
      cancelText="取消"
    >
      <Tabs defaultActiveKey="basic">
        <TabPane tab={<span><SettingOutlined />基本设置</span>} key="basic">
          <Form
            form={form}
            layout="vertical"
            className="mt-4"
          >
            <Form.Item
              name="title"
              label="区块标题"
              rules={[{ required: true, message: '请输入区块标题' }]}
            >
              <Input placeholder="请输入区块标题" />
            </Form.Item>

            <Form.Item
              name="description"
              label="区块描述"
              rules={[{ required: true, message: '请输入区块描述' }]}
            >
              <TextArea 
                rows={3} 
                placeholder="请输入区块描述"
              />
            </Form.Item>

            {blockType === 'chart' && (
              <Form.Item
                name="chartType"
                label="图表类型"
                rules={[{ required: true, message: '请选择图表类型' }]}
              >
                <Select placeholder="请选择图表类型">
                  <Option value="bar">柱状图</Option>
                  <Option value="line">折线图</Option>
                  <Option value="pie">饼图</Option>
                  <Option value="scatter">散点图</Option>
                </Select>
              </Form.Item>
            )}
          </Form>
        </TabPane>

        <TabPane tab={<span><CodeOutlined />UQM配置</span>} key="uqm">
          <div className="mt-4">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择模板
              </label>
              <Space>
                <Button 
                  size="small" 
                  onClick={() => handleTemplateSelect('it_employees')}
                >
                  IT员工查询
                </Button>
                <Button 
                  size="small" 
                  onClick={() => handleTemplateSelect('department_stats')}
                >
                  部门统计
                </Button>
              </Space>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                UQM查询配置 (JSON)
              </label>
              <TextArea
                value={uqmJson}
                onChange={(e) => {
                  setUqmJson(e.target.value);
                  validateJson(e.target.value);
                }}
                rows={15}
                placeholder="请输入UQM查询配置JSON"
                className={jsonError ? 'border-red-500' : ''}
              />
              {jsonError && (
                <div className="text-red-500 text-sm mt-1">{jsonError}</div>
              )}
            </div>
          </div>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default BlockConfigEditor; 