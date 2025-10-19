import { useState, useEffect } from 'react';
import { getAdminToken, isTokenValid, getTokenRemainingTime, refreshAdminToken } from '@/utils/auth';

export const useActivityAuth = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [remainingTime, setRemainingTime] = useState(0);
    const [isRefreshing, setIsRefreshing] = useState(false);

    useEffect(() => {
        // Check initial authentication status
        const checkAuth = () => {
            const valid = isTokenValid();
            setIsAuthenticated(valid);
            
            if (valid) {
                setRemainingTime(getTokenRemainingTime());
            }
        };

        checkAuth();

        // Update remaining time every minute
        const interval = setInterval(() => {
            if (isAuthenticated) {
                const time = getTokenRemainingTime();
                setRemainingTime(time);
                
                // If token is about to expire (less than 5 minutes), try to refresh
                if (time < 300 && time > 0) {
                    handleRefresh();
                }
            }
        }, 60000); // Check every minute

        return () => clearInterval(interval);
    }, [isAuthenticated]);

    const handleRefresh = async () => {
        if (isRefreshing) return;
        
        setIsRefreshing(true);
        try {
            const result = await refreshAdminToken();
            if (result.success) {
                setRemainingTime(getTokenRemainingTime());
                console.log('Token refreshed successfully');
            } else {
                console.log('Token refresh failed:', result.message);
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            setIsAuthenticated(false);
        } finally {
            setIsRefreshing(false);
        }
    };

    const formatTime = (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    };

    return {
        isAuthenticated,
        remainingTime,
        isRefreshing,
        refreshToken: handleRefresh,
        formatTime,
        token: getAdminToken()
    };
};
