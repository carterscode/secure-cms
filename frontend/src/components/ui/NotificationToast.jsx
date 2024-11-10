// frontend/src/components/ui/NotificationToast.jsx
import React, { useEffect } from 'react';
import { AlertCircle, CheckCircle2, XCircle, X } from 'lucide-react';
import { cn } from "@/lib/utils";

const NotificationToast = ({ 
  message, 
  type = 'info', 
  onClose, 
  duration = 5000,
  position = 'bottom-right'
}) => {
  useEffect(() => {
    if (duration) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: CheckCircle2,
    error: XCircle,
    info: AlertCircle,
    warning: AlertCircle
  };

  const Icon = icons[type];

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4'
  };

  const baseClasses = cn(
    "fixed max-w-md p-4 rounded-lg shadow-lg",
    "flex items-center space-x-3 z-50",
    "animate-in slide-in-from-right-full duration-300",
    positionClasses[position],
    {
      'bg-green-50 border border-green-200': type === 'success',
      'bg-red-50 border border-red-200': type === 'error',
      'bg-blue-50 border border-blue-200': type === 'info',
      'bg-yellow-50 border border-yellow-200': type === 'warning'
    }
  );

  const iconClasses = cn("h-5 w-5", {
    'text-green-600': type === 'success',
    'text-red-600': type === 'error',
    'text-blue-600': type === 'info',
    'text-yellow-600': type === 'warning'
  });

  return (
    <div className={baseClasses} role="alert">
      <Icon className={iconClasses} />
      <p className="text-sm flex-1">{message}</p>
      <button
        onClick={onClose}
        className="text-gray-500 hover:text-gray-700 focus:outline-none"
        aria-label="Close notification"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

// Toast Container for managing multiple toasts
const ToastContainer = ({ toasts, onClose }) => {
  return (
    <>
      {toasts.map((toast) => (
        <NotificationToast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => onClose(toast.id)}
          position={toast.position}
          duration={toast.duration}
        />
      ))}
    </>
  );
};

// Example usage:
// const [toasts, setToasts] = useState([]);
// 
// const addToast = (message, type = 'info') => {
//   const id = Date.now();
//   setToasts(prev => [...prev, { id, message, type }]);
// };
// 
// const removeToast = (id) => {
//   setToasts(prev => prev.filter(toast => toast.id !== id));
// };
//
// return <ToastContainer toasts={toasts} onClose={removeToast} />;

export { NotificationToast, ToastContainer };
