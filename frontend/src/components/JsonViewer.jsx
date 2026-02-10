import React from 'react'

const JsonViewer = ({ data }) => {
  const renderSimpleValue = (value) => {
    if (value === null) {
      return <span className="json-null">null</span>
    }

    if (typeof value === 'boolean') {
      return <span className="json-boolean">{String(value)}</span>
    }

    if (typeof value === 'number') {
      return <span className="json-number">{value}</span>
    }

    if (typeof value === 'string') {
      return <span className="json-string">{value}</span>
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="json-bracket">[]</span>
      }
      return (
        <div className="json-array-container">
          {value.map((item, index) => (
            <div key={index} className="json-array-item">
              {renderSimpleValue(item)}
            </div>
          ))}
        </div>
      )
    }

    if (typeof value === 'object') {
      const keys = Object.keys(value)
      if (keys.length === 0) {
        return <span className="json-bracket">{'{}'}</span>
      }
      return (
        <div className="json-nested-object">
          {keys.map((key) => (
            <div key={key} className="json-nested-property">
              <span className="json-key">{key}:</span>
              <span className="json-value">{renderSimpleValue(value[key])}</span>
            </div>
          ))}
        </div>
      )
    }

    return String(value)
  }

  const renderAsBoxes = () => {
    if (!data || typeof data !== 'object') {
      return <div className="json-value-box">{renderSimpleValue(data)}</div>
    }

    const keys = Object.keys(data)

    return (
      <div className="json-boxes-container">
        {keys.map((key) => (
          <div key={key} className="json-property-box">
            <div className="json-box-header">
              <span className="json-box-key">{key}</span>
            </div>
            <div className="json-box-content">
              {renderSimpleValue(data[key])}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return <div className="json-viewer">{renderAsBoxes()}</div>
}

export default JsonViewer
