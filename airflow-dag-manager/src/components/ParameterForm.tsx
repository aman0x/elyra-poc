import React, { useState, useCallback } from 'react';
import { DagParameters, ParameterField } from '../types/api';
import { airflowService } from '../services/airflowService';

interface ParameterFormProps {
  dagId: string;
  onSubmit: (parameters: DagParameters) => void;
  onCancel: () => void;
  loading?: boolean;
}

const ParameterForm: React.FC<ParameterFormProps> = ({
  dagId,
  onSubmit,
  onCancel,
  loading = false
}) => {
  // Toggle between form fields and raw JSON mode
  const [jsonMode, setJsonMode] = useState<boolean>(false);
  
  // Form field values
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  
  // Raw JSON input - Better default with example values
  const [jsonInput, setJsonInput] = useState<string>('{\n  "input_bucket": "",\n  "output_bucket": "",\n  "input_key": "",\n  "output_prefix": "",\n  "chain_transformations": true,\n  "update_raw_data": false\n}');
  
  // Validation states
  const [errors, setErrors] = useState<string[]>([]);
  const [jsonError, setJsonError] = useState<string>('');

  // Predefined common fields - you can customize these per DAG later
  const commonFields: ParameterField[] = [
    {
      name: 'input_bucket',
      label: 'Input Bucket',
      type: 'text',
      description: 'S3/MinIO bucket for input data'
    },
    {
      name: 'output_bucket',
      label: 'Output Bucket', 
      type: 'text',
      description: 'S3/MinIO bucket for output data'
    },
    {
      name: 'input_key',
      label: 'Input Key',
      type: 'text',
      description: 'Path to input file'
    },
    {
      name: 'output_prefix',
      label: 'Output Prefix',
      type: 'text',
      description: 'Output path prefix'
    },
    {
      name: 'chain_transformations',
      label: 'Chain Transformations',
      type: 'boolean',
      defaultValue: true
    },
    {
      name: 'update_raw_data',
      label: 'Update Raw Data',
      type: 'boolean',
      defaultValue: false
    }
  ];

  // Handle form field changes
  const handleFieldChange = useCallback((fieldName: string, value: any) => {
    setFormValues(prev => ({
      ...prev,
      [fieldName]: value
    }));
    setErrors([]); // Clear errors when user makes changes
  }, []);

  // Handle JSON input changes
  const handleJsonChange = useCallback((value: string) => {
    setJsonInput(value);
    setJsonError('');
    
    // Try to parse JSON to validate
    try {
      JSON.parse(value);
    } catch (error) {
      setJsonError('Invalid JSON format');
    }
  }, []);

  // Validate and prepare parameters
  const prepareParameters = useCallback((): DagParameters | null => {
    if (jsonMode) {
      // JSON mode - parse the raw JSON
      try {
        const parsed = JSON.parse(jsonInput);
        return parsed;
      } catch (error) {
        setJsonError('Invalid JSON format');
        return null;
      }
    } else {
      // Form mode - use form values
      const parameters: DagParameters = {};
      
      commonFields.forEach(field => {
        const value = formValues[field.name];
        if (value !== undefined && value !== '') {
          // Convert types appropriately
          if (field.type === 'number') {
            parameters[field.name] = Number(value);
          } else if (field.type === 'boolean') {
            parameters[field.name] = Boolean(value);
          } else {
            parameters[field.name] = value;
          }
        } else if (field.defaultValue !== undefined) {
          parameters[field.name] = field.defaultValue;
        }
      });
      
      return parameters;
    }
  }, [jsonMode, jsonInput, formValues, commonFields]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    
    const parameters = prepareParameters();
    if (!parameters) {
      return; // Validation errors already set
    }

    // Validate with airflow service
    const validation = airflowService.validateParameters(parameters);
    if (!validation.valid) {
      setErrors(validation.errors);
      return;
    }

    // Submit the parameters
    onSubmit(parameters);
  }, [prepareParameters, onSubmit]);

  // FIXED: Render form field based on type with proper boolean handling
  const renderField = (field: ParameterField) => {
    // Fix for boolean values - don't use || for default values
    const getValue = () => {
      if (formValues[field.name] !== undefined) {
        return formValues[field.name];
      }
      if (field.defaultValue !== undefined) {
        return field.defaultValue;
      }
      return field.type === 'boolean' ? false : '';
    };

    const value = getValue();

    switch (field.type) {
      case 'boolean':
        return (
          <label key={field.name} className="parameter-field boolean-field">
            <input
              type="checkbox"
              checked={Boolean(value)}
              onChange={(e) => handleFieldChange(field.name, e.target.checked)}
              disabled={loading}
            />
            <span className="field-label">{field.label}</span>
            {field.description && (
              <span className="field-description">{field.description}</span>
            )}
          </label>
        );

      case 'number':
        return (
          <div key={field.name} className="parameter-field">
            <label className="field-label">{field.label}</label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              disabled={loading}
              className="field-input"
            />
            {field.description && (
              <span className="field-description">{field.description}</span>
            )}
          </div>
        );

      default: // text
        return (
          <div key={field.name} className="parameter-field">
            <label className="field-label">{field.label}</label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              disabled={loading}
              className="field-input"
              placeholder={field.description}
            />
            {field.description && (
              <span className="field-description">{field.description}</span>
            )}
          </div>
        );
    }
  };

  return (
    <div className="parameter-form-container">
      <div className="parameter-form-header">
        <h3>Configure Parameters for {dagId}</h3>
        
        {/* Mode Toggle */}
        <div className="mode-toggle">
          <label>
            <input
              type="radio"
              name="mode"
              checked={!jsonMode}
              onChange={() => setJsonMode(false)}
              disabled={loading}
            />
            Form Fields
          </label>
          <label>
            <input
              type="radio"
              name="mode" 
              checked={jsonMode}
              onChange={() => setJsonMode(true)}
              disabled={loading}
            />
            Raw JSON
          </label>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="parameter-form">
        {jsonMode ? (
          // JSON Mode
          <div className="json-mode">
            <label className="field-label">Configuration JSON:</label>
            <textarea
              value={jsonInput}
              onChange={(e) => handleJsonChange(e.target.value)}
              className={`json-textarea ${jsonError ? 'error' : ''}`}
              rows={12}
              placeholder='{\n  "input_bucket": "my-bucket",\n  "input_key": "data/input.csv",\n  "chain_transformations": true\n}'
              disabled={loading}
            />
            {jsonError && (
              <div className="field-error">{jsonError}</div>
            )}
            <div className="json-help">
              <small>
                Enter valid JSON configuration. This will be passed as `dag_run.conf` to your DAG.
              </small>
            </div>
          </div>
        ) : (
          // Form Fields Mode  
          <div className="form-fields">
            <div className="fields-grid">
              {commonFields.map(renderField)}
            </div>
          </div>
        )}

        {/* Validation Errors */}
        {errors.length > 0 && (
          <div className="validation-errors">
            {errors.map((error, index) => (
              <div key={index} className="error-message">{error}</div>
            ))}
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="cancel-btn"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || (jsonMode && jsonError !== '')}
          >
            {loading ? 'Triggering...' : 'Trigger DAG'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ParameterForm;