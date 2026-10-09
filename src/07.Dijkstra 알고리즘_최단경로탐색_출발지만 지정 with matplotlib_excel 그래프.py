import heapq
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage

graph = {
    'A': {'B': 4, 'C': 1},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2, 'F': 6},
    'E': {'C': 10, 'D': 2, 'F': 3},
    'F': {'D': 6, 'E': 3},
}

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    
    queue = []
    heapq.heappush(queue, [distances[start], start])
    
    while queue:
        current_distance, current_destination = heapq.heappop(queue)
        
        if distances[current_destination] < current_distance:
            continue
        
        for new_destination, new_distance in graph[current_destination].items():
            distance = current_distance + new_distance
            if distance < distances[new_destination]:
                distances[new_destination] = distance
                heapq.heappush(queue, [distance, new_destination])
    
    return distances

def save_to_excel(start_node, distances, filename="dijkstra_result.xlsx"):
    """엑셀에 결과 저장"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = "다익스트라"
    
    # 제목
    ws['A1'] = "다익스트라 알고리즘 (최단경로탐색)"
    ws['A1'].font = Font(size=14, bold=True, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    ws.merge_cells('A1:C1')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 25
    
    # 시작점 정보
    ws['A3'] = "시작점"
    ws['B3'] = start_node
    ws['A3'].font = Font(bold=True, size=11)
    ws['B3'].font = Font(size=11)
    ws['A3'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    ws['B3'].fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    
    # 결과 테이블 헤더
    ws['A5'] = "노드"
    ws['B5'] = "최단거리"
    
    for col in ['A', 'B']:
        cell = ws[f'{col}5']
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # 데이터 정렬
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    
    # 데이터 입력
    row = 6
    for node, distance in sorted_distances:
        ws[f'A{row}'] = node
        if distance == float('inf'):
            ws[f'B{row}'] = "도달 불가"
        else:
            ws[f'B{row}'] = distance
        
        # 스타일
        for col in ['A', 'B']:
            cell = ws[f'{col}{row}']
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 시작점 강조
            if node == start_node:
                cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                cell.font = Font(bold=True)
        
        row += 1
    
    # 열 너비 설정
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 15
    
    # 그래프 정보 섹션
    graph_row = row + 2
    ws[f'A{graph_row}'] = "그래프 정보"
    ws[f'A{graph_row}'].font = Font(size=12, bold=True, color="FFFFFF")
    ws[f'A{graph_row}'].fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    ws.merge_cells(f'A{graph_row}:B{graph_row}')
    
    graph_row += 1
    ws[f'A{graph_row}'] = "노드 수"
    ws[f'B{graph_row}'] = len(graph)
    
    graph_row += 1
    ws[f'A{graph_row}'] = "총 엣지 수"
    total_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
    ws[f'B{graph_row}'] = total_edges
    
    # 그래프 구조 표시
    graph_row += 2
    ws[f'A{graph_row}'] = "그래프 구조"
    ws[f'A{graph_row}'].font = Font(size=11, bold=True)
    
    graph_row += 1
    for node, neighbors in sorted(graph.items()):
        neighbor_list = ', '.join([f"{n}({graph[node][n]})" for n in sorted(neighbors.keys())])
        ws[f'A{graph_row}'] = f"{node}: {neighbor_list}"
        graph_row += 1
    
    # 파일 저장
    wb.save(filename)
    print(f"✓ 저장: {filename}")

def print_results(start_node, distances):
    """콘솔에 결과 출력"""
    print("\n" + "="*50)
    print(f"다익스트라 알고리즘 (시작점: {start_node})")
    print("="*50)
    
    sorted_distances = sorted(distances.items(), key=lambda x: x[1])
    
    print(f"\n{'노드':<10}{'거리':<15}")
    print("-"*50)
    
    for node, distance in sorted_distances:
        if distance == float('inf'):
            print(f"{node:<10}{'도달 불가':<15}")
        else:
            print(f"{node:<10}{distance:<15.1f}")
    
    print("="*50 + "\n")

# 실행
if __name__ == "__main__":
    start_node = 'D'
    result = dijkstra(graph, start_node)
    
    # 콘솔 출력
    print_results(start_node, result)
    
    # 엑셀 저장
    print("엑셀 파일을 생성하고 있습니다...")
    save_to_excel(start_node, result, "dijkstra_result.xlsx")
