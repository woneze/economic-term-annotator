# styles.py
CSS_STYLE = """
<style>
    .term-highlight {
        background-color: #fff700;
        color: #333;
        font-weight: bold;
        padding: 0 4px;
        border-radius: 4px;
        cursor: help;
        border-bottom: 2px solid #ffcc00;
        position: relative;
        display: inline-block;
    }
    .term-highlight .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #2c3e50;
        color: #fff;
        text-align: left;
        border-radius: 8px;
        padding: 15px;
        position: absolute;
        z-index: 1000;
        bottom: 130%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.9rem;
        line-height: 1.5;
        font-weight: normal;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .term-highlight .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #2c3e50 transparent transparent transparent;
    }
    .term-highlight:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    .text-output {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        border: 1px solid #ddd;
        line-height: 2.0;
        font-size: 1.1rem;
    .summary-box {
        background-color: #f0f8ff; /* 아주 연한 파란색 (AliceBlue) */
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db; /* 왼쪽에 파란색 포인트 줄 */
        line-height: 1.8;
        font-size: 1.05rem;
        color: #2c3e50;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);    
    }
</style>
"""