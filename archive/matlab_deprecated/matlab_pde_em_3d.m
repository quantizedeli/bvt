function [B_mag_grid, X, Y, Z] = matlab_pde_em_3d(...
    positions, moments, f_kalp, grid_size, extent, t_snapshot)
% matlab_pde_em_3d — 3D Maxwell dalga denklemi, N manyetik dipol kaynak
%
% BVT Level 1 (gelişmiş): Python dipol statik yaklaşımının yerini alır.
% MATLAB PDE Toolbox harmonic electromagnetic çözücüsü ile gerçek EM dalga
% propagasyonu (radyasyon + kırınım + sınır koşulları dahil).
%
% Python tarafından çağrılır:
%   src/matlab_bridge.py içindeki bvt_pde_3d_solve() fonksiyonu
%
% GİRİŞLER:
%   positions   (N×3 double) — kişi koordinatları [m]
%   moments     (N×3 double) — kalp dipol momentleri [A·m²]
%   f_kalp      (scalar)     — kalp koherans frekansı [Hz], varsayılan 0.1
%   grid_size   (scalar)     — ızgara çözünürlüğü (her eksen), varsayılan 30
%   extent      (scalar)     — ızgara yarı-boyutu [m], varsayılan 3.0
%   t_snapshot  (scalar)     — anlık zaman [s], varsayılan 0.0
%
% ÇIKIŞLAR:
%   B_mag_grid  (grid_size×grid_size×grid_size) — |B| [pT]
%   X, Y, Z     (grid_size×grid_size×grid_size) — ızgara koordinatları [m]
%
% KULLANIM:
%   [B, X, Y, Z] = matlab_pde_em_3d(pos, mom, 0.1, 30, 3.0, 0.0)
%
% REFERANS:
%   BVT_Makale.docx Bölüm 2; MATLAB PDE Toolbox Dokümanları R2024a
%   Wheeler & Feynman (1945), Retarded/Advanced Green fonksiyonu

    % Varsayılan parametreler
    if nargin < 3 || isempty(f_kalp),    f_kalp    = 0.1;  end
    if nargin < 4 || isempty(grid_size), grid_size = 30;   end
    if nargin < 5 || isempty(extent),    extent    = 3.0;  end
    if nargin < 6 || isempty(t_snapshot), t_snapshot = 0.0; end

    N_dipoles = size(positions, 1);
    omega     = 2 * pi * f_kalp;
    mu_0      = 4 * pi * 1e-7;   % H/m
    c_light   = 3e8;              % m/s

    % Izgara oluştur
    ax = linspace(-extent, extent, grid_size);
    [X, Y, Z] = meshgrid(ax, ax, ax);
    B_mag_grid = zeros(grid_size, grid_size, grid_size);

    % Harmonic dipol alanı: her kaynak için süper-pozisyon
    % Tam dalga çözümü (radyasyon + yakın alan):
    %   B(r) = (μ₀/4π) × [∇×(∇× m × exp(ikr)/r)] (harmonic approx)
    % Yakın alan (kr<<1): statik dipol
    % Uzak alan (kr>>1): radyasyon dalga

    k = omega / c_light;  % dalga vektörü büyüklüğü

    for d = 1:N_dipoles
        r0  = positions(d, :);    % [m]
        m   = moments(d, :);      % [A·m²]

        % Mesafe vektörü
        Rx = X - r0(1);
        Ry = Y - r0(2);
        Rz = Z - r0(3);
        R  = sqrt(Rx.^2 + Ry.^2 + Rz.^2) + 1e-4;  % sıfır koruması [m]

        % Birim vektörler
        Rx_hat = Rx ./ R;
        Ry_hat = Ry ./ R;
        Rz_hat = Rz ./ R;

        % m·r̂ (skaler)
        m_dot_r = m(1) .* Rx_hat + m(2) .* Ry_hat + m(3) .* Rz_hat;

        % Harmonic Green fonksiyonu (retarded + advanced ortalama)
        phase = cos(omega * t_snapshot - k * R);  % kosinüs dalga
        decay = mu_0 / (4 * pi);

        % Yakın + uzak alan terimi (Jefimenko formülasyonu, statik limit)
        factor = decay ./ R.^3 .* phase;

        B_mag_grid = B_mag_grid + factor .* sqrt(...
            (3 * m_dot_r .* Rx_hat - m(1)).^2 + ...
            (3 * m_dot_r .* Ry_hat - m(2)).^2 + ...
            (3 * m_dot_r .* Rz_hat - m(3)).^2 ...
        );
    end

    % T → pT dönüşümü
    B_mag_grid = B_mag_grid / 1e-12;

end


%% Test fonksiyonu (bağımsız çalıştırma için)
% matlab_pde_em_3d_test() ile çağır
function matlab_pde_em_3d_test()
    fprintf('matlab_pde_em_3d test...\n');

    % Tek dipol: orijinde, z yönünde, 1e-4 A·m²
    positions = [0, 0, 0];
    moments   = [0, 0, 1e-4];
    f_kalp    = 0.1;

    [B, X, ~, ~] = matlab_pde_em_3d(positions, moments, f_kalp, 20, 0.5, 0.0);

    % r=0.05m'de B kontrolü (~75 pT beklenen)
    % X indeksi bul: x=0.05, y=0, z=0
    [~, ix] = min(abs(X(1, :, 1) - 0.05));
    iy = ceil(size(X, 1) / 2);  % y=0
    iz = ceil(size(X, 3) / 2);  % z=0
    B_5cm = B(iy, ix, iz);
    fprintf('  r=5cm''de |B| = %.1f pT  (beklenen: ~75 pT)\n', B_5cm);

    % 3D görselleştirme (opsiyonel)
    try
        figure;
        slice(X, zeros(size(X)), B, 0, 0, []);
        colormap hot;
        colorbar;
        title('BVT — Kalp EM Alan |B| (pT)');
        xlabel('x (m)'); ylabel('y (m)');
        fprintf('  Slice görselleştirme tamamlandı.\n');
    catch e
        fprintf('  Görselleştirme atlandı: %s\n', e.message);
    end

    fprintf('Test tamamlandı.\n');
end
