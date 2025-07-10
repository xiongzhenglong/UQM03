import React, { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { Result, Button } from 'antd';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="应用程序出现问题"
          subTitle={this.state.error?.message || '抱歉，出现了一个意外错误。'}
          extra={
            <Button type="primary" onClick={() => window.location.reload()}>
              重新加载页面
            </Button>
          }
        />
      );
    }

    return this.props.children;
  }
} 